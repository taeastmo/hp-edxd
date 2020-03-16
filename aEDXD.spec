# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['aEDXD.py'],
             pathex=['/Users/ross/Documents/GitHub/hp-edxd'],
             binaries=[],
             datas=[('/Users/ross/Documents/GitHub/hp-edxd/resources/stylesheet.qss',
                    'resources/'),
                    ('/Users/ross/Documents/GitHub/hp-edxd/aEDXD/resources/ABC.dat',
                    'aEDXD/resources/'),
                    ('/Users/ross/Documents/GitHub/hp-edxd/aEDXD/resources/MKL.dat',
                    'aEDXD/resources/'),
                    ('/Users/ross/Documents/GitHub/hp-edxd/aEDXD/resources/aEDXD_defaults.cfg',
                    'aEDXD/resources/')
                    ],
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
          name='aEDXD_run',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='aEDXD_run')

