from package_settings import NAME, VERSION, PACKAGES, DESCRIPTION
from setuptools import setup
from pathlib import Path
import json
import urllib.request
from functools import lru_cache


@lru_cache(maxsize=50)
def _get_github_sha(github_install_url: str):
    """From the github_install_url get the hash of the latest commit"""
    repository = Path(github_install_url).stem.split('#egg', 1)[0]
    organisation = Path(github_install_url).parent.stem
    with urllib.request.urlopen(f'https://api.github.com/repos/{organisation}/{repository}/commits/master') as response:
        return json.loads(response.read())['sha']


setup(
    name=NAME,
    version=VERSION,
    long_description=DESCRIPTION,
    author='Bloomsbury AI',
    author_email='contact@bloomsbury.ai',
    packages=PACKAGES,
    include_package_data=True,
    install_requires=[
        'Authomatic==0.1.0.post1',
        'beautifulsoup4==4.6.0',
        'markdown==2.6.11',
        'peewee==3.5.2',
        'pytest==3.6.4',
        'requests==2.18.1',
        'sanic==0.6.0',
        'numexpr==cfeae8ae246e95f23613e8b587746ed788b81f35',
        'cape.client==' + _get_github_sha(
            'git+https://github.com/bloomsburyai/cape-client#egg=cape.client'),
        'cape_userdb==' + _get_github_sha(
            'git+https://github.com/bloomsburyai/cape-userdb#egg=cape_userdb'),
        'cape_api_helpers==' + _get_github_sha(
            'git+https://github.com/bloomsburyai/cape-api-helpers#egg=cape_api_helpers'),
        'cape_responder==' + _get_github_sha(
            'git+https://github.com/bloomsburyai/cape-responder#egg=cape_responder'),
        'cape_document_manager==' + _get_github_sha(
            'git+https://github.com/bloomsburyai/cape-document-manager#egg=cape_document_manager'),
    ],
    dependency_links=[
        'git+https://github.com/pydata/numexpr#egg=numexpr-cfeae8ae246e95f23613e8b587746ed788b81f35',
        'git+https://github.com/bloomsburyai/cape-client#egg=cape.client-'+_get_github_sha(
            'git+https://github.com/bloomsburyai/cape-client#egg=cape.client'),
        'git+https://github.com/bloomsburyai/cape-userdb#egg=cape_userdb-' + _get_github_sha(
            'git+https://github.com/bloomsburyai/cape-userdb#egg=cape_userdb'),
        'git+https://github.com/bloomsburyai/cape-api-helpers#egg=cape_api_helpers-' + _get_github_sha(
            'git+https://github.com/bloomsburyai/cape-api-helpers#egg=cape_api_helpers'),
        'git+https://github.com/bloomsburyai/cape-responder#egg=cape_responder-' + _get_github_sha(
            'git+https://github.com/bloomsburyai/cape-responder#egg=cape_responder'),
        'git+https://github.com/bloomsburyai/cape-document-manager#egg=cape_document_manager-' + _get_github_sha(
            'git+https://github.com/bloomsburyai/cape-document-manager#egg=cape_document_manager'),
    ],
    package_data={
        '': ['*.*'],
    },
)
