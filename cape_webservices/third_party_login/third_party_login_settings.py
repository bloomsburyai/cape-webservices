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
