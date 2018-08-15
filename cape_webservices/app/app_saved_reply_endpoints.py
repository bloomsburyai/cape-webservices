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
from cape_webservices.app.app_settings import app_saved_reply_endpoints

from cape_webservices.app.app_middleware import respond_with_json, requires_auth
from cape_document_manager.annotation_store import AnnotationStore
from cape_api_helpers.output import list_response
from cape_api_helpers.input import required_parameter, optional_parameter, list_saved_reply_ids

_endpoint_route = lambda x: app_saved_reply_endpoints.route(URL_BASE + x, methods=['GET', 'POST'])

@_endpoint_route('/saved-replies/get-saved-replies')
@respond_with_json
@list_response
@list_saved_reply_ids
@requires_auth
def _get_saved_replies(request, number_of_items=30, offset=0, saved_reply_ids=None):
    user_token = request['user'].token
    search_term = optional_parameter(request, 'searchTerm', None)
    saved_replies = AnnotationStore.get_annotations(user_token, annotation_ids=saved_reply_ids,
                                                    search_term=search_term, saved_replies=True)
    return {'totalItems': len(saved_replies),
            'items': saved_replies[offset:offset+number_of_items]}


@_endpoint_route('/saved-replies/add-saved-reply')
@respond_with_json
@requires_auth
def _create_saved_reply(request):
    user_token = request['user'].token
    question = required_parameter(request, 'question')
    answer = required_parameter(request, 'answer')
    response = AnnotationStore.create_annotation(user_token, question, answer)
    return {'replyId': response['annotationId'], 'answerId': response['answerId']}


@_endpoint_route('/saved-replies/delete-saved-reply')
@respond_with_json
@requires_auth
def _delete_saved_reply(request):
    user_token = request['user'].token
    reply_id = required_parameter(request, 'replyId')
    AnnotationStore.delete_annotation(user_token, reply_id)
    return {'replyId': reply_id}


@_endpoint_route('/saved-replies/edit-canonical-question')
@respond_with_json
@requires_auth
def _edit_canonical_question(request):
    user_token = request['user'].token
    reply_id = required_parameter(request, 'replyId')
    question = required_parameter(request, 'question')
    AnnotationStore.edit_canonical_question(user_token, reply_id, question)
    return {'replyId': reply_id}


@_endpoint_route('/saved-replies/add-paraphrase-question')
@respond_with_json
@requires_auth
def _add_paraphrase_question(request):
    user_token = request['user'].token
    reply_id = required_parameter(request, 'replyId')
    question = required_parameter(request, 'question')
    return AnnotationStore.add_paraphrase_question(user_token, reply_id, question)


@_endpoint_route('/saved-replies/edit-paraphrase-question')
@respond_with_json
@requires_auth
def _edit_paraphrase_question(request):
    user_token = request['user'].token
    question_id = required_parameter(request, 'questionId')
    question = required_parameter(request, 'question')
    return AnnotationStore.edit_paraphrase_question(user_token, question_id, question)


@_endpoint_route('/saved-replies/delete-paraphrase-question')
@respond_with_json
@requires_auth
def _delete_paraphrase_question(request):
    user_token = request['user'].token
    question_id = required_parameter(request, 'questionId')
    return AnnotationStore.delete_paraphrase_question(user_token, question_id)


@_endpoint_route('/saved-replies/add-answer')
@respond_with_json
@requires_auth
def _add_answer(request):
    user_token = request['user'].token
    reply_id = required_parameter(request, 'replyId')
    answer = required_parameter(request, 'answer')
    return AnnotationStore.add_answer(user_token, reply_id, answer)


@_endpoint_route('/saved-replies/edit-answer')
@respond_with_json
@requires_auth
def _edit_answer(request):
    user_token = request['user'].token
    answer_id = required_parameter(request, 'answerId')
    answer = required_parameter(request, 'answer')
    return AnnotationStore.edit_answer(user_token, answer_id, answer)


@_endpoint_route('/saved-replies/delete-answer')
@respond_with_json
@requires_auth
def _delete_answer(request):
    user_token = request['user'].token
    answer_id = required_parameter(request, 'answerId')
    return AnnotationStore.delete_answer(user_token, answer_id)


if __name__ == '__main__':
    # import sanic.response
    #
    # # Create a fake request
    # request = {
    #     "user": {
    #         "token": "test_user_token",
    #     },
    #     "args": {
    #         "token": '0b2f8518af6211e7a6219801a7ae6c69',
    #         "question": 'What is a potato?',
    #         "answer": 'A potato is a vegetable',
    #     }
    # }
    # response: sanic.response.HTTPResponse = _create_saved_reply(request)
    # print(response.body)
    pass
