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

API_VERSION = '0.1'
URL_BASE = '/api/' + API_VERSION

app_endpoints = Blueprint('app_endpoints')
app_annotation_endpoints = Blueprint('app_annotation_endpoints')
app_document_endpoints = Blueprint('app_document_endpoints')
app_saved_reply_endpoints = Blueprint('app_saved_reply_endpoints')
app_inbox_endpoints = Blueprint('app_inbox_endpoints')
app_user_endpoints = Blueprint('app_user_endpoints')