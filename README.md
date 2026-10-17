# MTG Prices 2.0

Локальный сайт для учёта карт Magic: The Gathering: количество, название, сет, цена в долларах, рублях и MTGO tix, история цены.
Цены берутся с [StarCityGames](https://starcitygames.com), [MTGGoldfish](https://www.mtggoldfish.com) и [Scryfall](https://scryfall.com).
Сайт работает на вашем компьютере и открывается в браузере, поэтому годится для Linux, Windows и macOS.

Возможности:

- добавление карт списком (`количество ссылка` в каждой строке) или из Excel (.xlsx);
- обновление цены одной карты или всех карт вкладки в фоне, с прогрессом и кнопкой «Остановить»;
  незавершённые задачи продолжаются после перезапуска;
- история цены каждой карты с графиком, изменение с прошлой проверки в таблице;
- автообновление всех цен раз в N часов и курса ЦБ РФ (пока запущен сайт);
- курс доллара вручную или кнопкой «Курс ЦБ»; цена в рублях = цена в долларах, округлённая вверх, × курс;
- поиск по названию и сету, итоги в долларах и рублях;
- выгрузка в Excel: одна книга, по листу на сайт.

### Ссылки на карты

| Сайт | Пример | Замечания |
|---|---|---|
| StarCityGames | `https://starcitygames.com/...-enf/?sku=SGL-MTG-CMR-334-ENF1` | фойл определяется по SKU |
| MTGGoldfish | `https://www.mtggoldfish.com/price/The+Brothers+War:Foil/Loran+of+the+Third+Path` | бумажная цена в $, MTGO в tix |
| Scryfall | `https://scryfall.com/card/bro/12/loran-of-the-third-path` | цены из API; `#foil` или `#etched` в конце ссылки выбирают вариант |

## Запуск

Нужен Python 3.12+ и [uv](https://docs.astral.sh/uv/) (или pip).

```bash
uv sync
uv run mtgprices                 # откроет http://127.0.0.1:8000 в браузере
uv run mtgprices --port 9000 --no-browser
```

Без uv: `pip install .` и затем `mtgprices`.

Данные хранятся в `~/.local/share/mtgprices/cards.db` (Windows: `%LOCALAPPDATA%\mtgprices`, macOS: `~/Library/Application Support/mtgprices`).
Другую папку можно задать через `--data-dir` (перед командой) или переменную `MTGPRICES_DATA_DIR`.

### Перенос данных из Qt-версии 1.x

```bash
uv run mtgprices import-legacy resources/cards.db
```

Команда переносит карты и курс из `resources/data.config`. Повторный запуск ничего не дублирует.

### Доступ с других устройств

По умолчанию сайт доступен только с этого компьютера. Для доступа из домашней сети нужен пароль
(вход через стандартное окно браузера, имя пользователя любое):

```bash
MTGPRICES_PASSWORD='придумайте-пароль' uv run mtgprices --host 0.0.0.0 --allowed-host 192.168.1.10
```

`--allowed-host` — IP или имя этого компьютера, по которому к нему обращаются. Пароль передаётся по HTTP без шифрования,
поэтому открывайте сайт только в доверенной сети. Запуск без пароля возможен только с явным флагом `--no-password`.

### Docker

```bash
docker build -t mtgprices .
docker run -d -p 127.0.0.1:8000:8000 -v mtgprices-data:/data mtgprices
```

Для доступа из сети добавьте `-e MTGPRICES_PASSWORD=...`, опубликуйте порт как `-p 8000:8000`
и передайте `--allowed-host` в команде запуска.

### Исполняемый файл

```bash
uv sync --group build
uv run pyinstaller mtgprices.spec    # результат в dist/
```

Собирать нужно на той ОС, для которой нужен файл; CI собирает файлы для Linux, Windows и macOS по тегу `v*`
или ручному запуску. Запуск exe поднимает сайт и открывает браузер.

## Разработка

```bash
uv run pytest              # все тесты без сети
uv run pytest -m network   # проверка парсеров и курса ЦБ на живых сайтах
uv run ruff check . && uv run ruff format --check .
uv run mypy
```

## Технологии

Python, FastAPI, Jinja2, SQLite, httpx, BeautifulSoup, openpyxl, pytest, ruff, mypy.
