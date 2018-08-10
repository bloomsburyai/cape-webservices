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

from cape_webservices.app.app_settings import URL_BASE
from cape_webservices.app.app_settings import app_inbox_endpoints

from cape_webservices.app.app_middleware import respond_with_json, requires_auth
from cape_userdb.event import Event
from cape_api_helpers.exceptions import UserException
from cape_api_helpers.output import list_response
from cape_api_helpers.input import required_parameter, optional_parameter
from cape_api_helpers.text_responses import *

_endpoint_route = lambda x: app_inbox_endpoints.route(URL_BASE + x, methods=['GET', 'POST'])


@_endpoint_route('/inbox/get-inbox')
@requires_auth
@list_response
@respond_with_json
def _get_inbox(request, number_of_items=30, offset=0):
    user_id = request['user'].user_id
    read = optional_parameter(request, 'read', 'both').lower()
    answered = optional_parameter(request, 'answered', 'both').lower()
    search_term = optional_parameter(request, 'searchTerm', None)

    events_query = Event.select().where(Event.user_id == user_id, Event.archived == False)
    if read == 'true':
        events_query = events_query.where(Event.read == True)
    elif read == 'false':
        events_query = events_query.where(Event.read == False)
    if answered == 'true':
        events_query = events_query.where(Event.answered == True)
    elif answered == 'false':
        events_query = events_query.where(Event.answered == False)
    if search_term is not None:
        events_query = events_query.where(Event.question.contains(search_term))

    events = []
    total_items = events_query.count()
    for event in events_query.limit(number_of_items).order_by(Event.created.desc()).offset(offset):
        events.append({
            'id': str(event.id),
            'question': event.question,
            'read': event.read,
            'answered': event.answered,
            'answers': event.answers,
            'created': event.created,
            'modified': event.modified,
            'questionSource': event.question_source
        })

    return {"totalItems": total_items, "items": events}


@_endpoint_route('/inbox/mark-inbox-read')
@requires_auth
@respond_with_json
def _mark_inbox_read(request):
    inbox_id = required_parameter(request, 'inboxId')
    if not inbox_id.isnumeric():
        raise UserException(ERROR_INBOX_DOES_NOT_EXIST % inbox_id)
    event = Event.get('id', int(inbox_id))
    if event is None:
        raise UserException(ERROR_INBOX_DOES_NOT_EXIST % inbox_id)
    event.read = True
    event.save()

    return {'inboxId': inbox_id}


@_endpoint_route('/inbox/archive-inbox')
@requires_auth
@respond_with_json
def _archive_inbox(request):
    inbox_id = required_parameter(request, 'inboxId')
    if not inbox_id.isnumeric():
        raise UserException(ERROR_INBOX_DOES_NOT_EXIST % inbox_id)
    event = Event.get('id', int(inbox_id))
    if event is None:
        raise UserException(ERROR_INBOX_DOES_NOT_EXIST % inbox_id)
    event.archived = True
    event.save()

    return {'inboxId': inbox_id}
