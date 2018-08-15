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

from sanic import Blueprint
from sanic.response import json as jsonify
from functools import partial
from cape_api_helpers.headers import generate_cors_headers
from cape_webservices.app.app_middleware import status

configuration_endpoints = Blueprint('configuration_endpoints')
_endpoint_route = partial(configuration_endpoints.route, methods=['GET', 'POST'])


@_endpoint_route('/status')
async def _version(request):
    return jsonify(status(request), headers=generate_cors_headers(request))
