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
import os
import time

from cape_api_helpers.exceptions import UserException
from cape_api_helpers.input import required_parameter, optional_parameter, list_document_ids
from cape_api_helpers.output import list_response, debuggable
from cape_api_helpers.text_responses import *

from cape_responder.responder_core import Responder
from cape_webservices.webservices_settings import MAX_SIZE_INLINE_TEXT, \
    HOSTNAME, CONFIG_SERVER, MAX_NUMBER_OF_ANSWERS
from cape_responder.task_manager import connect
from cape_webservices.app.app_middleware import respond_with_json, requires_token
from cape_webservices.app.app_settings import URL_BASE
from cape_webservices.app.app_settings import app_endpoints
from cape_userdb.base import DB
from cape_userdb.event import Event
from cape_userdb.coverage import Coverage

_endpoint_route = lambda x: app_endpoints.route(URL_BASE + x, methods=['GET', 'POST'])


def square(x):
    return x ** 2


def neg(x):
    return -x


def store_event(user_id, question, answers, question_source, answered, duration, automatic=False):
    if DB.is_closed():
        DB.connect()
    event = Event(user_id=user_id, question=question, question_source=question_source, answers=answers,
                  answered=answered, duration=duration, automatic=automatic)
    event.save()
    total = Event.select().where(Event.user_id == user_id).count()
    automatic = Event.select().where(Event.user_id == user_id, Event.automatic == True).count()
    # Base line of 60% from MR plus proportion answered by saved replies
    coverage = 60 + (automatic / total) * 35
    coverage_stat = Coverage(user_id=user_id, coverage=coverage)
    coverage_stat.save()
    DB.close()


@_endpoint_route('/test')
@debuggable
@respond_with_json
def _test(request):
    client = connect()
    A = client.map(square, range(10))
    B = client.map(neg, A)
    total = client.submit(sum, B)
    return {'worker': os.getpid(), "token": request["args"]["token"], 'result': total.result(),
            'hostname': HOSTNAME, 'port': CONFIG_SERVER['port']}





@_endpoint_route('/answer')
@debuggable
@respond_with_json
@list_response
@list_document_ids
@requires_token
def _answer(request, number_of_items=1, offset=0, document_ids=None, max_number_of_answers=MAX_NUMBER_OF_ANSWERS):
    start_time = time.time()
    number_of_items = min(number_of_items, max(0, max_number_of_answers - offset))
    user_token = required_parameter(request, 'token')
    question = required_parameter(request, 'question')
    source_type = optional_parameter(request, 'sourceType', 'all').lower()
    text = optional_parameter(request, 'text', None)
    speed_or_accuracy = optional_parameter(request, 'speedOrAccuracy', 'balanced').lower()
    saved_reply_threshold = optional_parameter(request, 'threshold', request['user_from_token'].saved_reply_threshold)
    document_threshold = optional_parameter(request, 'threshold', request['user_from_token'].document_threshold)
    if source_type not in {'document', 'saved_reply', 'all'}:
        raise UserException(ERROR_INVALID_SOURCE_TYPE)
    if speed_or_accuracy not in {'speed', 'accuracy', 'balanced', 'total'}:
        raise UserException(ERROR_INVALID_SPEED_OR_ACCURACY % speed_or_accuracy)
    else:
        if request['user_from_token'].plan == "pro":
            speed_or_accuracy = "total"
    if text is not None and len(text) > MAX_SIZE_INLINE_TEXT:
        raise UserException(ERROR_MAX_SIZE_INLINE_TEXT % (MAX_SIZE_INLINE_TEXT, len(text)))
    preview = "" if text is None else f"Text: {text[:25]}...{text[25:]}\n"
    results = []

    if source_type != 'document':
        results.extend(Responder.get_answers_from_similar_questions(user_token, question, source_type, document_ids,saved_reply_threshold))

    results = sorted(results, key=lambda x: x['confidence'],
                     reverse=True)

    if (source_type == 'document' or source_type == 'all') and len(results) < number_of_items:
        results.extend(Responder.get_answers_from_documents(user_token,
                                                            question,
                                                            document_ids,
                                                            offset,
                                                            number_of_items - len(results),
                                                            text,document_threshold))

    results = results[offset:offset + number_of_items]

    automatic = False
    if len(results) > 0:
        automatic = results[0]['sourceType'] == 'saved_reply' or results[0]['sourceType'] == 'annotation'

    duration = time.time() - start_time
    connect().submit(store_event,
                     request['user_from_token'].user_id,
                     question,
                     results,
                     'API',
                     len(results) > 0,
                     duration,
                     automatic)

    return {'items': results}


if __name__ == '__main__':
    import sanic.response


    # Create a fake request
    class MyDict(dict):
        pass


    request = MyDict({
        "args": {
            # 'token': '1WVr2R5WiQ4SrFSZQ16TVjHY731skPX1YIEKNqQg5so',
            'token': 'testtoken_answer',
            'question': 'Who is Luis Ulloa?',
            'threshold': 'low',
            'documentIds': '',
            'sourcetype': 'document',
            'speedoraccuracy': '',
            'numberofitems': '1',
            'offset': '0'
        }
    })
    request.headers = {}

    response: sanic.response.HTTPResponse = _answer(request)
    response_dict = json.loads(response.body.decode('utf-8'))

    for i, item in enumerate(response_dict['result']['items']):
        print("{} | {} | {} | {}".format(i + 1, item['text'], item['sourceType'], item['confidence']))
