# -*- mode: python ; coding: utf-8 -*-

import sys
sys.setrecursionlimit(5000)
__version__ = '0.5.0'
from sys import platform as _platform

block_cipher = None

import burnman
burnman_path = os.path.dirname(burnman.__file__)

import epics
epics_path = os.path.dirname(epics.__file__)

extra_datas = [
    ("hpm/resources", "hpm/resources"),
    (os.path.join(burnman_path, "data"), "burnman/data")
]

platform = ''
extra_binaries=[]

if _platform == "linux" or _platform == "linux2":
    platform = "Linux"
    name = "hpMCA"
elif _platform == "win32" or _platform == "cygwin":
    platform = "Win"
    name = "hpMCA.exe"
elif _platform == "darwin":
    platform = "Mac"
    extra_binaries=[ ( os.path.join(epics_path, 'clibs','darwin64','libca.dylib') , '.' ),
            ( os.path.join(epics_path, 'clibs','darwin64','libComPYEPICS.dylib'), '.' )
                ]
    name = "run_hpMCA"



a = Analysis(['hpMCA.py'],
             pathex=['/Users/ross/Documents/GitHub/hp-edxd'],
             binaries=extra_binaries,
             datas=extra_datas,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

# remove packages which are not needed by Dioptas
# a.binaries = [x for x in a.binaries if not x[0].startswith("matplotlib")]
a.binaries = [x for x in a.binaries if not x[0].startswith("zmq")]
a.binaries = [x for x in a.binaries if not x[0].startswith("IPython")]
a.binaries = [x for x in a.binaries if not x[0].startswith("docutils")]
a.binaries = [x for x in a.binaries if not x[0].startswith("pytz")]
a.binaries = [x for x in a.binaries if not x[0].startswith("wx")]
a.binaries = [x for x in a.binaries if not x[0].startswith("libQtWebKit")]
a.binaries = [x for x in a.binaries if not x[0].startswith("libQtDesigner")]
a.binaries = [x for x in a.binaries if not x[0].startswith("PySide")]
a.binaries = [x for x in a.binaries if not x[0].startswith("libtk")]

exclude_datas = [
    "IPython",
#   "matplotlib",
#   "mpl-data", #needs to be included
#   "_MEI",
#   "docutils",
#   "pytz",
#   "lib",
   "include",
   "sphinx",
#   ".py",
   "tests",
   "skimage",
   "alabaster",
   "boto",
   "jsonschema",
   "babel",
   "idlelib",
   "requests",
   "qt4_plugins",
   "qt5_plugins"
]

for exclude_data in exclude_datas:
    a.datas = [x for x in a.datas if exclude_data not in x[0]]


pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='hpMCA',
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
               name='hpMCA')

if _platform == "darwin":
    app = BUNDLE(coll,
                 name='hpMCA_{}.app'.format(__version__)
                 
                 )