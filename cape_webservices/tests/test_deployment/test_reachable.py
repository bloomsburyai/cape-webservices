import pytest
import requests

from cape_webservices.tests.tests_settings import URL

_REACHABLE_ENDPOINTS = [
    "/",
    "/index.html",
    "/status",
]


@pytest.mark.parametrize("endpoint", _REACHABLE_ENDPOINTS)
def test_reachable(endpoint):
    session = requests.Session()
    response = session.get(URL + endpoint)
    assert response.status_code == 200


@pytest.mark.parametrize("endpoint_location", [
    "/kaboom",
    "/HolaCapitan",
])
def test_error_redirection(endpoint_location):
    session = requests.Session()
    response = session.get(URL + endpoint_location, allow_redirects=False)
    assert response.status_code == 500
    assert response.json()['success'] == False
