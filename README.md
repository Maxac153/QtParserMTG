# QtParserMTG 1.1

## О проекте

### Описание

Приложение предназначено для хранение информации о картах (количество, название карты, название сете, цена в долларах, цена в рублях, ссылка).
Целью приложения является сбор информации для продажи карт, мониторинга цен, создание выходной Excel таблицы.

### Технологии

- Python 3.10.9
- PyQt5
- SQLite
- BeautifulSoup
- Pandas

## Запуск приложения
<img src="img/launch.PNG" width="800">

Запустите exe файл приложения находящийся в папке ParsCard.

<img src="img/main_window.PNG" width="700">

Главное окно после запуска программы.

<img src="img/parsing_card.PNG" width="700">

После добавление количества карт и ссылок в Text Edit их можно будет добавить в таблицу.

### Описание кнопок
- $  - Перерасчёт цены в рублях;
- 🗘 - Обновление цен карт;
- 🗑  - Удаление всех карт из таблиц;

## Будущие изменения

- [ ] Добавление multiprocessing, для ускорения парсинга;
- [x] Сделать сборку приложения под Linux;
- [ ] Сделать сборку приложения под Win7;
- [ ] Собранный инсталлятора с помощью NSIS;
- [ ] Добавить поис по названию и фильтры;
- [x] Переделать взаимодействие с БД;

## Ссылки для скачивания образа:
- Win10: https://drive.google.com/drive/folders/1uhbKDeVflzhq1C1IXs3DfskdX0zLIN8I?usp=sharing;
- licux: https://drive.google.com/drive/folders/1-U582XKN_1L-_ozhqEDlCGYh426gJqbB?usp=sharing.
