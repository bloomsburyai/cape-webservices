from authomatic.adapters import BaseAdapter
from urllib.parse import urlparse

from cape_responder.manage_users import create_user

from logging import debug
from cape_userdb.user import User
from cape_userdb.session import Session
from cape_api_helpers.input import optional_parameter
from cape_api_helpers.exceptions import UserException
from cape_api_helpers.text_responses import *
from sanic import response
from sanic.response import redirect
from secrets import token_urlsafe

_COOKIE_EXPIRES = 2592000


class SanicAdapter(BaseAdapter):
    """Adapter for the |sanic|_ package."""

    def __init__(self, request, response):
        """
        :param request:
            A |sanic|_ :class:`Request` instance.

        :param response:
            A |sanic|_ :class:`Response` instance.
        """
        self.request = request
        self.response = response

    # ===========================================================================
    # Response
    # ===========================================================================

    def write(self, value):
        debug("writting body of sanic session adapter", value)
        self.response.body += value

    def set_header(self, key, value):
        debug("setting header of sanic session adapter", key, value)
        self.response.headers[key] = value

    def set_status(self, status):
        debug("setting status of sanic session adapter", status)
        self.response.status = int(status[:3])

    # ===========================================================================
    # Request
    # ===========================================================================

    @property
    def params(self):
        return dict(self.request.raw_args)

    @property
    def url(self):
        parsed = urlparse(self.request.url)
        # because of ssl termination after the load balancer we force the https scheme
        return f"https://{parsed.netloc}{parsed.path}"

    @property
    def cookies(self):
        return dict(self.request.cookies)


def upsert_login_redirect(request, user_id: str, third_party_info: dict, success_cb: str, adapter):
    debug('Login', user_id, 'with', third_party_info, success_cb)
    user_or_none: User = User.get('user_id', user_id)
    if user_or_none is None:
        user_or_none = create_user(user_id=user_id, password=str(token_urlsafe()), third_party_info=third_party_info)
    session_obj: Session = Session.create(user_id=user_or_none.user_id)
    request['session_id'] = session_obj.session_id
    return redirect(success_cb)


def set_callback_cookies(resp, success_cb, error_cb):
    resp.cookies['successCallback'] = success_cb
    resp.cookies['successCallback']['expires'] = _COOKIE_EXPIRES
    resp.cookies['successCallback']['httponly'] = True
    resp.cookies['errorCallback'] = error_cb
    resp.cookies['errorCallback']['expires'] = _COOKIE_EXPIRES
    resp.cookies['errorCallback']['httponly'] = True


def oauth_init(request):
    success_cb = optional_parameter(request, 'successCallback', None)
    error_cb = optional_parameter(request, 'errorCallback', None)
    if success_cb is None and 'successCallback' not in request.cookies:
        raise UserException(ERROR_REQUIRED_PARAMETER % 'successCallback')
    if error_cb is None and 'errorCallback' not in request.cookies:
        raise UserException(ERROR_REQUIRED_PARAMETER % 'errorCallback')

    if 'oauthSession' not in request.cookies:
        # Set a cookie and reload this path so that the load balancer can redirect us back to this node after OAuth
        first_response = response.redirect(request.path)
        first_response.cookies['oauthSession'] = token_urlsafe()
        first_response.cookies['oauthSession']['expires'] = _COOKIE_EXPIRES
        first_response.cookies['oauthSession']['httponly'] = True
        set_callback_cookies(first_response, success_cb, error_cb)
        return success_cb, error_cb, None, first_response

    adapter = SanicAdapter(request, response.html(body=""))

    if success_cb and error_cb:
        set_callback_cookies(adapter.response, success_cb, error_cb)
    else:
        success_cb = request.cookies['successCallback']
        error_cb = request.cookies['errorCallback']

    return success_cb, error_cb, adapter, None
