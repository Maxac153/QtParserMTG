import asyncio
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager, suppress
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Annotated, Any
from urllib.parse import urlencode

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.trustedhost import TrustedHostMiddleware

from mtgprices.config import Settings
from mtgprices.errors import CardNotFoundError, ImportFileError, InvalidLinkError, MtgPricesError
from mtgprices.excel import export_workbook, read_links
from mtgprices.fetcher import Fetcher
from mtgprices.jobs import JobManager, job_to_dict
from mtgprices.links import check_quantity, parse_links_text, validate_link
from mtgprices.models import Card, LinkInput, Site
from mtgprices.pricing import format_amount, parse_rate, ruble_price
from mtgprices.rates import fetch_cbr_usd_rate
from mtgprices.repository import CardRepository
from mtgprices.scheduler import Scheduler, load_auto_settings, save_auto_settings
from mtgprices.service import CardService, PageFetcher
from mtgprices.web.charts import price_chart
from mtgprices.web.security import PasswordMiddleware, SameOriginMiddleware

WEB_DIR = Path(__file__).parent

# Сообщения передаются в адресе кодом, а не текстом, чтобы ссылкой нельзя было подсунуть свой текст
NOTICES = {
    "rate_saved": ("ok", "Курс сохранён"),
    "rate_invalid": ("error", "Курс должен быть положительным числом"),
    "rate_cbr_failed": ("error", "Не удалось получить курс ЦБ РФ, попробуйте позже"),
    "auto_saved": ("ok", "Настройки автообновления сохранены"),
    "auto_invalid": ("error", "Интервал автообновления должен быть целым числом часов от 0 до 720"),
    "nothing_to_add": ("error", "Не найдено ни одной ссылки"),
    "import_invalid": ("error", "Не удалось прочитать файл: нужен .xlsx не больше 5 МБ"),
    "card_refreshed": ("ok", "Цена обновлена"),
    "card_refresh_failed": ("error", "Не удалось обновить цену, причина указана в строке карты"),
    "card_deleted": ("ok", "Карта удалена"),
    "quantity_saved": ("ok", "Количество сохранено"),
    "quantity_invalid": ("error", "Количество должно быть целым числом от 1"),
    "all_deleted": ("ok", "Все карты вкладки удалены"),
    "nothing_to_refresh": ("error", "На вкладке нет карт"),
}

JOB_ADD = "add"
JOB_REFRESH = "refresh"

RateFetcher = Callable[[], Awaitable[Decimal]]


@dataclass(frozen=True)
class Totals:
    quantity: int
    usd: Decimal
    rub: Decimal


def compute_totals(cards: list[Card], rate: Decimal) -> Totals:
    priced = [(card, card.price_usd) for card in cards if card.price_usd is not None]
    return Totals(
        quantity=sum(card.quantity for card in cards),
        usd=sum((price * card.quantity for card, price in priced), Decimal(0)),
        rub=sum((ruble_price(price, rate) * card.quantity for card, price in priced), Decimal(0)),
    )


def format_time(value: str | None) -> str:
    if not value:
        return "—"
    return datetime.fromisoformat(value).astimezone().strftime("%d.%m.%Y %H:%M")


def format_change(card: Card) -> tuple[str, str] | None:
    """Изменение цены с прошлой проверки: (css-класс, текст) или None."""
    if card.price_usd is None or card.previous_price_usd is None or card.price_usd == card.previous_price_usd:
        return None
    delta = card.price_usd - card.previous_price_usd
    sign = "+" if delta > 0 else "−"
    return ("up" if delta > 0 else "down", f"{sign}{format_amount(abs(delta))}")


def card_to_dict(card: Card, rate: Decimal) -> dict[str, Any]:
    return {
        "id": card.id,
        "site": card.site,
        "url": card.url,
        "quantity": card.quantity,
        "name": card.name,
        "set_name": card.set_name,
        "price_usd": None if card.price_usd is None else str(card.price_usd),
        "price_rub": None if card.price_usd is None else str(ruble_price(card.price_usd, rate)),
        "price_tix": None if card.price_tix is None else str(card.price_tix),
        "previous_price_usd": None if card.previous_price_usd is None else str(card.previous_price_usd),
        "updated_at": card.updated_at,
        "last_error": card.last_error,
    }


def create_app(
    settings: Settings | None = None,
    fetcher: PageFetcher | None = None,
    rate_fetcher: RateFetcher | None = None,
) -> FastAPI:
    settings = settings or Settings()
    repo = CardRepository(settings.db_path)
    jobs = JobManager(repo, settings.concurrency)
    get_cbr_rate: RateFetcher = rate_fetcher or (lambda: fetch_cbr_usd_rate(timeout=settings.request_timeout))

    def start_refresh(site: Site | None = None) -> str | None:
        ids = repo.card_ids(site)
        if not ids:
            return None
        where = site.label if site else "всех карт"
        return jobs.start(JOB_REFRESH, f"Обновление цен: {where} ({len(ids)})", ids)

    def start_scheduled_refresh() -> str | None:
        # Не запускаем второе обновление поверх идущего
        return None if jobs.running(JOB_REFRESH) else start_refresh()

    scheduler = Scheduler(repo, start_scheduled_refresh, get_cbr_rate, check_every=settings.scheduler_interval or 60)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        repo.init()
        own_fetcher: Fetcher | None = None
        active_fetcher: PageFetcher
        if fetcher is None:
            own_fetcher = active_fetcher = Fetcher(timeout=settings.request_timeout)
        else:
            active_fetcher = fetcher
        service = CardService(repo, active_fetcher)
        app.state.service = service
        jobs.register(JOB_ADD, service.add_card_job_item)
        jobs.register(JOB_REFRESH, service.refresh_card_job_item)
        jobs.resume()
        scheduler_task = asyncio.create_task(scheduler.run()) if settings.scheduler_interval else None
        try:
            yield
        finally:
            if scheduler_task is not None:
                scheduler_task.cancel()
                with suppress(asyncio.CancelledError):
                    await scheduler_task
            await jobs.shutdown()
            if own_fetcher is not None:
                await own_fetcher.aclose()

    app = FastAPI(title="MTG Prices", lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
    # Последний добавленный middleware выполняется первым: Host → пароль → same-origin
    app.add_middleware(SameOriginMiddleware)
    if settings.password:
        app.add_middleware(PasswordMiddleware, password=settings.password)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)
    app.mount("/static", StaticFiles(directory=WEB_DIR / "static"), name="static")
    app.state.repo = repo
    app.state.jobs = jobs
    app.state.scheduler = scheduler

    templates = Jinja2Templates(directory=WEB_DIR / "templates")
    templates.env.filters["amount"] = format_amount
    templates.env.filters["time"] = format_time
    templates.env.globals["ruble_price"] = ruble_price
    templates.env.globals["price_change"] = format_change

    def service(request: Request) -> CardService:
        return request.app.state.service

    def back(site: Site | None = None, q: str = "", **extra: str) -> RedirectResponse:
        params = {key: value for key, value in {"site": site or "", "q": q, **extra}.items() if value}
        return RedirectResponse("/?" + urlencode(params) if params else "/", status_code=303)

    def start_add_job(items: list[LinkInput], errors: list[str]) -> RedirectResponse:
        if not items and not errors:
            return back(notice="nothing_to_add")
        payloads = [{"quantity": item.quantity, "url": item.url} for item in items]
        job_id = jobs.start(JOB_ADD, f"Добавление карт ({len(items)})", payloads, errors)
        return back(validate_link(items[0].url) if items else None, job=job_id)

    def get_card_or_404(card_id: int) -> Card:
        try:
            return repo.get(card_id)
        except CardNotFoundError as exc:
            raise HTTPException(404, str(exc)) from exc

    # --- страницы ---

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request, site: Site | None = None, q: str = "", job: str = "", notice: str = ""):
        counts = repo.count_by_site()
        if site is None:
            site = next((s for s in Site if counts[s]), Site.STARCITYGAMES)
        cards = repo.list_cards(site, q)
        rate = repo.get_rate()
        current_job = jobs.get(job) if job else None
        running = [j for j in jobs.running() if current_job is None or j.id != current_job.id]
        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "sites": list(Site),
                "site": site,
                "counts": counts,
                "cards": cards,
                "show_tix": any(card.price_tix is not None for card in cards),
                "q": q,
                "rate": rate,
                "auto": load_auto_settings(repo),
                "totals": compute_totals(cards, rate),
                "job": current_job,
                "running_jobs": running,
                "notice": NOTICES.get(notice),
            },
        )

    @app.get("/cards/{card_id}", response_class=HTMLResponse)
    async def card_page(request: Request, card_id: int):
        card = get_card_or_404(card_id)
        history = repo.price_history(card_id)
        return templates.TemplateResponse(
            request,
            "card.html",
            {
                "card": card,
                "rate": repo.get_rate(),
                "history": list(reversed(history)),
                "chart": price_chart(history),
            },
        )

    # --- карты ---

    @app.post("/cards/add")
    async def add_cards(links: Annotated[str, Form()] = ""):
        return start_add_job(*parse_links_text(links))

    @app.post("/cards/import")
    async def import_cards(file: Annotated[UploadFile, File()]):
        data = await file.read(settings.max_upload_bytes + 1)
        if len(data) > settings.max_upload_bytes:
            return back(notice="import_invalid")
        try:
            items, errors = read_links(data)
        except ImportFileError:
            return back(notice="import_invalid")
        return start_add_job(items, errors)

    @app.post("/cards/{card_id}/refresh")
    async def refresh_card(request: Request, card_id: int, q: Annotated[str, Form()] = ""):
        card = get_card_or_404(card_id)
        try:
            await service(request).refresh_card(card_id)
        except MtgPricesError:
            return back(card.site, q, notice="card_refresh_failed")
        return back(card.site, q, notice="card_refreshed")

    @app.post("/cards/{card_id}/quantity")
    async def set_quantity(card_id: int, quantity: Annotated[str, Form()], q: Annotated[str, Form()] = ""):
        card = get_card_or_404(card_id)
        try:
            repo.set_quantity(card_id, check_quantity(int(quantity)))
        except (ValueError, InvalidLinkError):
            return back(card.site, q, notice="quantity_invalid")
        return back(card.site, q, notice="quantity_saved")

    @app.post("/cards/{card_id}/delete")
    async def delete_card(card_id: int, q: Annotated[str, Form()] = ""):
        card = get_card_or_404(card_id)
        repo.delete(card_id)
        return back(card.site, q, notice="card_deleted")

    @app.post("/sites/{site}/refresh")
    async def refresh_site(site: Site):
        job_id = start_refresh(site)
        if job_id is None:
            return back(site, notice="nothing_to_refresh")
        return back(site, job=job_id)

    @app.post("/sites/{site}/delete")
    async def delete_site(site: Site):
        repo.delete_all(site)
        return back(site, notice="all_deleted")

    # --- настройки и экспорт ---

    @app.post("/settings/rate")
    async def save_rate(rate: Annotated[str, Form()], site: Annotated[Site | None, Form()] = None):
        try:
            repo.set_rate(parse_rate(rate))
        except ValueError:
            return back(site, notice="rate_invalid")
        return back(site, notice="rate_saved")

    @app.post("/settings/rate/cbr")
    async def load_cbr_rate(site: Annotated[Site | None, Form()] = None):
        rate = await scheduler.update_rate()
        return back(site, notice="rate_saved" if rate is not None else "rate_cbr_failed")

    @app.post("/settings/auto")
    async def save_auto(
        refresh_hours: Annotated[str, Form()] = "0",
        auto_rate: Annotated[str | None, Form()] = None,
        site: Annotated[Site | None, Form()] = None,
    ):
        try:
            save_auto_settings(repo, int(refresh_hours or 0), auto_rate is not None)
        except ValueError:
            return back(site, notice="auto_invalid")
        return back(site, notice="auto_saved")

    @app.get("/export.xlsx")
    async def export():
        data = export_workbook({site: repo.list_cards(site) for site in Site}, repo.get_rate())
        filename = f"mtg-cards-{datetime.now():%Y-%m-%d}.xlsx"
        return Response(
            data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    # --- задачи ---

    @app.post("/jobs/{job_id}/cancel")
    async def cancel_job(job_id: str):
        job = jobs.cancel(job_id)
        if job is None:
            raise HTTPException(404, "Задача не найдена")
        return back(job=job.id)

    # --- JSON API ---

    @app.get("/api/jobs/{job_id}")
    async def job_status(job_id: str):
        job = jobs.get(job_id)
        if job is None:
            raise HTTPException(404, "Задача не найдена")
        return job_to_dict(job)

    @app.get("/api/cards")
    async def api_cards(site: Site | None = None, q: str = ""):
        rate = repo.get_rate()
        return JSONResponse([card_to_dict(card, rate) for card in repo.list_cards(site, q)])

    @app.get("/api/cards/{card_id}/history")
    async def api_history(card_id: int):
        get_card_or_404(card_id)
        return [
            {
                "checked_at": point.checked_at,
                "price_usd": None if point.price_usd is None else str(point.price_usd),
                "price_tix": None if point.price_tix is None else str(point.price_tix),
            }
            for point in repo.price_history(card_id)
        ]

    return app
