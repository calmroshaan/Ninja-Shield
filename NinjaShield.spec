# -*- mode: python ; coding: utf-8 -*-


from PyInstaller.utils.hooks import collect_all
playwright_datas, playwright_binaries, playwright_hiddenimports = collect_all('playwright')

a = Analysis(
    ['gui.py'],
    pathex=[],
    binaries=playwright_binaries,
    datas=[('icon.ico', '.')] + playwright_datas,
    hiddenimports=playwright_hiddenimports + [    'playwright',
    'playwright.async_api',
    'playwright._impl._api_types',
    'playwright._impl._browser_context',
    'browser_launcher',
    'fingerprint_engine',
    'license_manager',
    'asyncio',
    'urllib.parse',
    'urllib.request',],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='NinjaShield',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='NinjaShield',
)
