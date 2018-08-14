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

import json
from functools import wraps

from cape_api_helpers.exceptions import UserException
from cape_api_helpers.api_helpers_settings import SECRET_EXTRA_INFO_KEYWORD
from logging import debug
from sanic.response import json as jsonify
from sanic.response import text as textify
from cape_webservices.app.app_settings import app_endpoints, URL_BASE
from cape_userdb.user import User
from cape_userdb.session import Session
from cape_userdb.base import DB
from cape_api_helpers.input import required_parameter, optional_parameter
from cape_api_helpers.text_responses import *
from cape_api_helpers.headers import generate_cors_headers
from cape_webservices import version
from cape_webservices import webservices_settings
from cape_webservices import webapp_core

_SESSION_COOKIE_NAME = 'session'
_SESSION_COOKIE_EXPIRES = 2592000
_MUST_BE_GET_PARAM = {'admintoken', 'token'}  # because these are used in routing, post are not allowed
# Google and facebook require query parameters to be specified in advance in the allowed refer list, so we only accept
# these as POST parameters
_MUST_BE_POST_PARAM = {'successcallback', 'errorcallback'}
_SLACK_TYPES = {'event_callback', 'url_verification'}


def status(request):
    return {'version': version.VERSION, 'name': version.NAME,
            'hostname': webservices_settings.HOSTNAME,
            'port': webservices_settings.CONFIG_SERVER['port'],
            'headers': dict(request.headers),
            'client_ip': request.headers.get('x-client-ip', request.ip),
            'url_params': request['args'],
            'plugins': webapp_core.enabled_plugins
            }


def respond_with_json(decorated):
    @wraps(decorated)
    def wrapper(request, *args, **kw):
        status = 200
        result = decorated(request, *args, **kw)
        if 'success' not in result:
            result = {'success': True, 'result': result}
        return jsonify(result, status=status, headers=generate_cors_headers(request))

    return wrapper


def respond_with_plain_json(decorated):
    @wraps(decorated)
    def wrapper(request, *args, **kw):
        status = 200
        result = decorated(request, *args, **kw)
        return jsonify(result, status=status, headers=generate_cors_headers(request))

    return wrapper


def respond_with_text(decorated):
    @wraps(decorated)
    def wrapper(request, *args, **kw):
        status = 200
        result = decorated(request, *args, **kw)
        return textify(result, status=status, headers=generate_cors_headers(request))

    return wrapper


def _is_sanic_static(response) -> bool:
    """Determine if the request headers correspond to a static sanic resource"""
    if isinstance(response, list):
        return False
    return response.status == 304 or 'Last-Modified' in response.headers


@app_endpoints.middleware('response')
async def _after_request(request, response):
    DB.close()
    if _is_sanic_static(response):
        return
    if 'args' in request and SECRET_EXTRA_INFO_KEYWORD in request['args']:
        try:
            body_dict = json.loads(response.body)
            body_dict.update({'request_info': status(request)})
            response.body = jsonify(body_dict).body
        except Exception:
            pass

    # if there is no session, delete cookie
    if 'session_id' not in request and _SESSION_COOKIE_NAME in request.cookies:
        session = Session.get('session_id', request.cookies.get(_SESSION_COOKIE_NAME, 'invalid'))
        if session is not None:
            session.delete_instance()
        debug('Deleting cookie')
        response.cookies[_SESSION_COOKIE_NAME] = ''
        response.cookies[_SESSION_COOKIE_NAME]['expires'] = 0
        response.cookies[_SESSION_COOKIE_NAME]['max-age'] = 0

    # If session id has changed
    elif request.get('session_id', False) and \
            request['session_id'] != request.cookies.get(_SESSION_COOKIE_NAME, 'invalid'):
        debug('Saving session in cookie %s', request['session_id'])
        response.cookies[_SESSION_COOKIE_NAME] = request['session_id']
        response.cookies[_SESSION_COOKIE_NAME]['expires'] = _SESSION_COOKIE_EXPIRES
        response.cookies[_SESSION_COOKIE_NAME]['httponly'] = True

    if not request.path.startswith('/status'):
        debug(f'Endpoint {request.path} ')


@app_endpoints.middleware('request')
async def _before_request(request):
    """Respond to preflight CORS requests and load parameters."""
    if request.method == "OPTIONS":
        return textify("ok", headers=generate_cors_headers(request))
    request['args'] = {}
    if request.form:
        for key in request.form:
            key_lower = key.lower()
            if key_lower in _MUST_BE_GET_PARAM and not request.path.startswith(URL_BASE + '/email/'):
                raise UserException(CANNOT_BE_POST_PARAM % key)
            request['args'][key_lower] = request.form[key][0]
    elif request.json:
        slack_message = ('type' in request.json and request.json['type'] in _SLACK_TYPES)
        for key in request.json:
            key_lower = key.lower()
            if slack_message:
                request['args'][key_lower] = request.json[key]
            else:
                if key_lower in _MUST_BE_GET_PARAM and not request.path.startswith('/hangouts/'):
                    raise UserException(CANNOT_BE_POST_PARAM % key)
                # Make all url parameters strings
                if isinstance(request.json[key], dict):
                    request['args'][key_lower] = json.dumps(request.json[key])
                elif isinstance(request.json[key], list):
                    request['args'][key_lower] = json.dumps(request.json[key])
                else:
                    request['args'][key_lower] = str(request.json[key])
    # Take all Get parameters
    for key, value in list(request.raw_args.items()):
        key_lower = key.lower()
        if key_lower in _MUST_BE_POST_PARAM:
            raise UserException(CANNOT_BE_GET_PARAM % key)
        request['args'][key_lower] = value


@app_endpoints.middleware('request')
async def _add_user_to_request(request):
    if DB.is_closed():
        DB.connect()
    if 'admintoken' in request['args']:
        user = User.get('admin_token', request['args']['admintoken'])
        if user is None:
            return None
        request['user'] = user
    else:
        sid = request.cookies.get(_SESSION_COOKIE_NAME, 'invalid')
        session_or_none: Session = Session.get('session_id', sid)
        if session_or_none is None:
            return None
        request['user'] = User.get('user_id', session_or_none.user_id)
        request['session_id'] = session_or_none.session_id


def requires_auth(wrapped):
    @wraps(wrapped)
    def decorated(request, *args, **kwargs):
        if 'user' not in request:
            raise UserException(NOT_LOGGED_TEXT)
        return wrapped(request, *args, **kwargs)

    return decorated


def requires_token(wrapped):
    """Decorator that accepts both login and token."""

    @wraps(wrapped)
    def decorated(request, *args, **kwargs):
        token = optional_parameter(request, 'token', None)
        if token is None:
            if 'user' in request:
                request['user_from_token'] = request['user']
                request['args']['token'] = request['user'].token
                return wrapped(request, *args, **kwargs)
            else:
                required_parameter(request, 'token')
        user = User.get('token', token)
        if user is not None:
            request['user_from_token'] = user
            return wrapped(request, *args, **kwargs)
        else:
            raise UserException(INVALID_TOKEN % token)

    return decorated


def requires_admin(wrapped):
    """Checks that the superAdminToken has been supplied before allowing access to admin methods."""

    @wraps(wrapped)
    def decorated(request, *args, **kwargs):
        if 'superadmintoken' in request['args'] and request['args'][
            'superadmintoken'] == webservices_settings.SUPER_ADMIN_TOKEN:
            return wrapped(request, *args, **kwargs)
        else:
            raise UserException(ADMIN_ONLY)

    return decorated
