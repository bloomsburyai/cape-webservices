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
