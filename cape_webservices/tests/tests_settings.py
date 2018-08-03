import os
from cape_webservices.webservices_settings import CONFIG_SERVER

URL = os.getenv('CAPE_TEST_HOST', f'http://localhost:{CONFIG_SERVER["port"]}')
