# -*- mode: python ; coding: utf-8 -*-
# Сборка одного исполняемого файла: uv run --group build pyinstaller mtgprices.spec
# Готовый файл появится в dist/. Собирать нужно на той ОС, под которую нужен файл.
from PyInstaller.utils.hooks import collect_submodules

a = Analysis(
    ['mtgprices/__main__.py'],
    pathex=['.'],
    datas=[
        ('mtgprices/web/templates', 'mtgprices/web/templates'),
        ('mtgprices/web/static', 'mtgprices/web/static'),
    ],
    # uvicorn подгружает реализации цикла и протоколов по имени
    hiddenimports=collect_submodules('uvicorn'),
    excludes=['tkinter'],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='MTGPrices',
    debug=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    # Окно консоли показывает адрес сайта; закрытие окна останавливает сервер
    console=True,
    icon=['logo/logo.ico'],
)
