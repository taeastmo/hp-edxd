

import subprocess
import sys
from os.path import dirname, join, exists, realpath

PY2 = sys.version_info < (3, 0, 0)

FRAMEWORK = subprocess.Popen(
    '/usr/libexec/java_home',
    stdout=subprocess.PIPE, shell=True).communicate()[0]

if not PY2:
    FRAMEWORK = FRAMEWORK.decode('utf-8')

FRAMEWORK = FRAMEWORK.strip()

if not FRAMEWORK:
    print('You must install Java on your Mac OS X distro')

if '1.6' in FRAMEWORK:
    LIB_LOCATION = '../Libraries/libjvm.dylib'
    INCLUDE_DIRS = [join(
        FRAMEWORK, (
            'System/Library/Frameworks/'
            'JavaVM.framework/Versions/Current/Headers'
        )
    )]