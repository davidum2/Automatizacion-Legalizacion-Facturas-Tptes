# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
import os

datas = []
datas += collect_data_files('babel')

if os.path.exists('app_icon.ico'):
    datas.append(('app_icon.ico', '.'))

hiddenimports = [
    'babel.numbers',
    'babel.dates',
    'babel.core',
    'tkcalendar',
    'docx',
    'docx2pdf',
    'openpyxl',
    'pandas',
    'fpdf',
    'selenium',
    'selenium.webdriver',
    'selenium.webdriver.chrome.service',
    'selenium.webdriver.chrome.options',
    'win32com.client',
    'pythoncom',
    'core.xml_processor',
    'core.document_generator',
    'core.excel_reader',
    'generators.creacionDocumentos',
    'ui.config_personal_tab',
    'ui.date_selector',
    'utils.file_utils',
    'utils.formatters',
    'utils.pdf_utils',
    'utils.web_utils',
]

a = Analysis(
    ['main-app.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'IPython', 'jupyter', 'notebook', 'torch', 'torchvision',
        'scipy', 'matplotlib', 'playwright', 'PyQt6', 'PySide6',
        'grpc', 'sympy', 'sklearn', 'cv2', 'opencv-python'
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LegalizacionFacturasTptes',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico' if os.path.exists('app_icon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='LegalizacionFacturasTptes',
)
