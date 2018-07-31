from authomatic.providers import oauth2, oauth1
from random import random

oauth1.Twitter.user_info_url = 'https://api.twitter.com/1.1/account/verify_credentials.json?include_email=true'

CONFIG = {
    'fb': {

        'class_': oauth2.Facebook,
        'id': 2,
        # Facebook is an AuthorizationProvider too.
        'consumer_key': 'REPLACEME',
        'consumer_secret': 'REPLACEME',

        # But it is also an OAuth 2.0 provider and it needs scope.
        'scope': ['public_profile', 'email'],
    },

    'google': {

        'class_': oauth2.Google,
        'id': 1,
        # Google is an AuthorizationProvider too.
        'consumer_key': 'REPLACEME.apps.googleusercontent.com',
        'consumer_secret': 'REPLACEME',

        # But it is also an OAuth 2.0 provider and it needs scope.
        'scope': oauth2.Google.user_info_scope,
    },

    'github': {

        'class_': oauth2.GitHub,
        'consumer_key': 'REPLACEME',
        'consumer_secret': 'REPLACEME',
        'scope': oauth2.GitHub.user_info_scope + ['user:email'],
        'access_headers': {'User-Agent': 'bloogram.com-App'},  # XXX mandatory
    },

    'twitter': {

        'class_': oauth1.Twitter,
        'consumer_key': 'REPLACEME',
        'consumer_secret': 'REPLACEME',
    },

}

SECRET_SALT = str(random())
