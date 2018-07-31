import os
import subprocess
from urllib.parse import urlparse

from setuptools import find_packages

_THIS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__)))
_README_FILEPATH = os.path.join(_THIS_FOLDER, 'README.md')
if os.path.isfile(_README_FILEPATH):
    with open(_README_FILEPATH) as file_pointer:
        DESCRIPTION = file_pointer.read()
else:
    DESCRIPTION = ''

# setup tools renames the folders so this does not work : os.path.split(THIS_FOLDER)[1]
_origin = subprocess.check_output(['git', 'config', '--get', 'remote.origin.url']).strip().decode()
NAME = os.path.split(urlparse(_origin).path)[1]
VERSION = subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip().decode()

PACKAGES = find_packages()
_VERSION_FILEPATH = os.path.join(_THIS_FOLDER, PACKAGES[0], 'version.py')
with open(_VERSION_FILEPATH, 'w') as version_file:
    version_file.write(f"""
VERSION = ""\"{VERSION}""\"
NAME = ""\"{NAME}""\"
DESCRIPTION = ""\"{DESCRIPTION}""\"
    """)
