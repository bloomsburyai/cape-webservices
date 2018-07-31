from sanic import Blueprint
from sanic.exceptions import NotFound, RequestTimeout,InvalidUsage
from sanic.response import json as jsonify
from functools import partial

from logging import debug, warning
from cape_api_helpers.headers import generate_cors_headers
from cape_api_helpers.exceptions import UserException
from cape_api_helpers.text_responses import *
import secrets
import json
errors_endpoints = Blueprint('errors_endpoints')

_endpoint_route = partial(errors_endpoints.route, methods=['GET', 'POST'])


@errors_endpoints.exception(NotFound)
def _404(request, exception):
    return jsonify({'success': False, 'result': {'message': NOT_FOUND_TEXT}}, status=500, headers=generate_cors_headers(request))


@errors_endpoints.exception(RequestTimeout)
def _timeout(request, exception):
    return jsonify({'success': False, 'result': {'message': TIMEOUT_TEXT}}, status=500, headers=generate_cors_headers(request))


@errors_endpoints.exception(Exception)
def _500(request, exception):
    error_id = secrets.token_urlsafe(32)
    if exception.__class__ is UserException:
        debug("User exception: %s" % exception.message, exc_info=True)
        message = exception.message
    elif exception.__class__ is json.JSONDecodeError:
        debug(ERROR_INVALID_JSON, exc_info=True,error_id=error_id)
        message = ERROR_INVALID_JSON
    elif exception.__class__ is InvalidUsage :
        debug(ERROR_INVALID_USAGE, exc_info=True)
        message = ERROR_INVALID_USAGE
    else:
        warning("Exception in API", exc_info=True)
        message = ERROR_TEXT
    return jsonify({'success': False, 'result': {'message': message,'errorId':error_id}},
                   status=500, headers=generate_cors_headers(request))


@_endpoint_route('/kaboom')
async def _kaboom(request):
    return 1 / 0
