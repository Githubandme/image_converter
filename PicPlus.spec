# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['e:\\PicPlus-Converter\\src\\image_converter.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\win\\AppData\\Local\\Programs\\Python\\Python313\\Lib\\site-packages\\pillow_avif', 'pillow_avif'), ('C:\\Users\\win\\AppData\\Local\\Programs\\Python\\Python313\\Lib\\site-packages\\PIL', 'PIL'), ('C:\\Users\\win\\AppData\\Local\\Programs\\Python\\Python313\\Lib\\site-packages\\PySide6', 'PySide6')],
    hiddenimports=['pillow_avif', 'PySide6'],
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
    a.binaries,
    a.datas,
    [],
    name='PicPlus',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['e:\\PicPlus-Converter\\assets\\picpp_icon.ico'],
)
