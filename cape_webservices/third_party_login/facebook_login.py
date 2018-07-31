import json

from authomatic import Authomatic
from cape_webservices.third_party_login.third_party_login_settings import CONFIG, SECRET_SALT
from cape_webservices.third_party_login.third_party_login_core import SanicAdapter, \
    upsert_login_redirect, oauth_init
from sanic import response
from cape_webservices.app.app_settings import URL_BASE
from cape_webservices.app.app_settings import app_endpoints
from cape_api_helpers.input import optional_parameter
from cape_api_helpers.exceptions import UserException
from cape_api_helpers.text_responses import *
from logging import debug, warning

_endpoint_route = lambda x: app_endpoints.route(URL_BASE + x, methods=['GET', 'POST'])


@_endpoint_route('/user/facebook-oauth2callback')
async def redirect_login_record_session_google(request):
    success_cb, error_cb, adapter, first_response = oauth_init(request)

    if adapter is None:
        return first_response

    authomatic = Authomatic(config=CONFIG, secret=SECRET_SALT)

    result = authomatic.login(adapter, 'fb',
                              # session=session['authomatic'],
                              session_saver=lambda: None)

    if result:
        if result.error:
            warning("FB login error", result.error)
            return response.redirect('%s?error=%s' % (error_cb, result.error))
        elif result.user:
            debug("FB login success", result.user)
            result.user.update()
            user_dict = result.user.__dict__
            debug("FB retrieving email", user_dict)
            rea = authomatic.access(result.user.credentials,
                                    'https://graph.facebook.com/' + result.user.id + '?fields=email')
            user_email = json.loads(rea.read().decode('utf-8'))["email"]
            debug("FB login update success", result.user)
            return upsert_login_redirect(request, "facebook:" + user_email,
                                         {'email': user_email,
                                          'id': user_dict['id'],
                                          'username': user_dict['username'],
                                          'name': user_dict['name'],
                                          'first_name': user_dict['first_name'],
                                          'last_name': user_dict['last_name'],
                                          'nickname': user_dict['nickname'],
                                          'link': user_dict['link'],
                                          'gender': user_dict['gender'],
                                          'timezone': user_dict['timezone'],
                                          'locale': user_dict['locale'],
                                          'birth_date': user_dict['birth_date'],
                                          'country': user_dict['country'],
                                          'city': user_dict['city'],
                                          'location': user_dict['location'],
                                          'postal_code': user_dict['postal_code'],
                                          'picture': user_dict['picture'],
                                          'phone': user_dict['phone'],
                                          }, success_cb, adapter)
    return adapter.response
