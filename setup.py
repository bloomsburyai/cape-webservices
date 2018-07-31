import os
import sys
import subprocess
from package_settings import NAME, VERSION, PACKAGES, DESCRIPTION
from setuptools import setup

# TODO is there a better way ? dependencies seem to always require the version
# Calling only at the egg_info step gives us the wanted depth first behavior
if 'egg_info' in sys.argv and os.getenv('CAPE_DEPENDENCIES', 'False').lower() == 'true':
    subprocess.check_call(['pip3', 'install','--no-warn-conflicts','--upgrade', '-r', 'requirements.txt'])

setup(
    name=NAME,
    version=VERSION,
    long_description=DESCRIPTION,
    author='Bloomsbury AI',
    author_email='contact@bloomsbury.ai',
    packages=PACKAGES,
    include_package_data=True,
    package_data={
        '': ['*.*'],
    },
)
