"""Фоновые задачи (добавление карт, обновление цен) с прогрессом и отменой.

Состояние задач хранится в БД: после перезапуска сервера незавершённые задачи
продолжаются с необработанных элементов.
"""

import asyncio
import logging
import uuid
from collections.abc import Awaitable, Callable, Sequence
from enum import StrEnum
from typing import Any

from mtgprices.errors import MtgPricesError
from mtgprices.repository import CardRepository, JobRecord

log = logging.getLogger(__name__)

Worker = Callable[[Any], Awaitable[object]]


class JobStatus(StrEnum):
    RUNNING = "running"
    FINISHED = "finished"
    CANCELLED = "cancelled"


def job_to_dict(job: JobRecord) -> dict[str, Any]:
    return {
        "id": job.id,
        "kind": job.kind,
        "title": job.title,
        "total": job.total,
        "done": job.done,
        "succeeded": job.succeeded,
        "errors": job.errors,
        "status": job.status,
    }


class JobManager:
    def __init__(self, store: CardRepository, concurrency: int = 4):
        self.store = store
        self.concurrency = max(1, concurrency)
        self._workers: dict[str, Worker] = {}
        self._cancel: dict[str, asyncio.Event] = {}
        self._tasks: set[asyncio.Task[None]] = set()

    def register(self, kind: str, worker: Worker) -> None:
        """worker получает payload элемента (то, что передали в start, после JSON)."""
        self._workers[kind] = worker

    def start(self, kind: str, title: str, payloads: Sequence[object], errors: Sequence[str] = ()) -> str:
        """Запускает задачу. errors — ошибки, найденные ещё до запуска (например, при разборе ввода)."""
        if kind not in self._workers:
            raise ValueError(f"Неизвестный тип задачи: {kind}")
        job_id = uuid.uuid4().hex
        self.store.create_job(job_id, kind, title, payloads, errors)
        self._launch(job_id, kind)
        return job_id

    def resume(self) -> int:
        """Продолжает задачи, прерванные остановкой сервера."""
        resumed = 0
        for job in self.store.jobs_with_status(JobStatus.RUNNING):
            if job.id in self._cancel:
                continue
            if job.kind not in self._workers:
                self.store.set_job_status(job.id, JobStatus.CANCELLED)
                continue
            self._launch(job.id, job.kind)
            resumed += 1
        return resumed

    def get(self, job_id: str) -> JobRecord | None:
        return self.store.get_job(job_id)

    def cancel(self, job_id: str) -> JobRecord | None:
        event = self._cancel.get(job_id)
        if event is not None:
            event.set()
        return self.store.get_job(job_id)

    def running(self, kind: str | None = None) -> list[JobRecord]:
        return [
            job
            for job in self.store.jobs_with_status(JobStatus.RUNNING)
            if job.id in self._cancel and (kind is None or job.kind == kind)
        ]

    async def wait_all(self) -> None:
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)

    async def shutdown(self) -> None:
        # Задачи прерываются, но остаются «running» в БД и продолжатся при следующем запуске
        for task in self._tasks:
            task.cancel()
        await self.wait_all()

    def _launch(self, job_id: str, kind: str) -> None:
        self._cancel[job_id] = asyncio.Event()
        task = asyncio.create_task(self._run(job_id, self._workers[kind]))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def _run(self, job_id: str, worker: Worker) -> None:
        cancel_event = self._cancel[job_id]
        queue: asyncio.Queue[tuple[int, object]] = asyncio.Queue()
        for item in self.store.pending_job_items(job_id):
            queue.put_nowait(item)

        async def consume() -> None:
            # Отмена проверяется перед каждым элементом; начатые запросы доводятся до конца
            while not cancel_event.is_set():
                try:
                    seq, payload = queue.get_nowait()
                except asyncio.QueueEmpty:
                    return
                error: str | None = None
                try:
                    await worker(payload)
                except MtgPricesError as exc:
                    error = str(exc)
                except Exception:
                    log.exception("Ошибка при обработке %r", payload)
                    error = f"Внутренняя ошибка при обработке {payload}"
                self.store.finish_job_item(job_id, seq, error)

        try:
            await asyncio.gather(*(consume() for _ in range(min(self.concurrency, max(queue.qsize(), 1)))))
            cancelled = cancel_event.is_set() and bool(self.store.pending_job_items(job_id))
            self.store.set_job_status(job_id, JobStatus.CANCELLED if cancelled else JobStatus.FINISHED)
        finally:
            del self._cancel[job_id]
