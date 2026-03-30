# bg_remover.spec
# Build a standalone Windows EXE:
#   pip install pyinstaller
#   pyinstaller bg_remover.spec

from PyInstaller.utils.hooks import copy_metadata

# Metadatas to prevent "PackageNotFoundError"
my_datas = []
my_datas += copy_metadata('pymatting')
my_datas += copy_metadata('rembg')
my_datas += copy_metadata('onnxruntime')

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=['.'],
    binaries=[],
    datas=my_datas, # <-- Passed the metadata here
    hiddenimports=[
        'rembg',
        'onnxruntime',
        'customtkinter',
        'PIL',
        'PIL._tkinter_finder',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='BGEraser',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,     # No console window
    icon=None,         # Replace with 'icon.ico' if you have one
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BGEraser',
)