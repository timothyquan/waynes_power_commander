# -*- mode: python ; coding: utf-8 -*-
import sys
sys.setrecursionlimit(3000)

block_cipher = None


a = Analysis(['waynes_power_commander.py'],
             pathex=['Z:\\09-Software - Except Bridge Systems\\waynes_power_commander'],
             binaries=[],
             datas=[('wayne.ico', '.'), ('settings.yaml.TEMPLATE', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='waynes_power_commander',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          icon='Z:\\09-Software - Except Bridge Systems\\waynes_power_commander\\wayne.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='waynes_power_commander')
