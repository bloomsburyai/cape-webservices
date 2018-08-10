# Copyright 2018 BLEMUNDSBURY AI LIMITED
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
