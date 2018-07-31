from typing import List
from hashlib import sha256
from cape_webservices.app.app_settings import URL_BASE
from cape_webservices.app.app_settings import app_annotation_endpoints
from cape_webservices.app.app_middleware import respond_with_json, requires_auth
from cape_document_manager.annotation_store import AnnotationStore
from cape_api_helpers.output import list_response
from cape_api_helpers.input import required_parameter, optional_parameter, list_annotation_ids, list_document_ids, \
    list_pages, dict_metadata
from cape_api_helpers.exceptions import UserException
from cape_api_helpers.text_responses import ERROR_ANNOTATION_MISSING_PARAMS

_endpoint_route = lambda x: app_annotation_endpoints.route(URL_BASE + x, methods=['GET', 'POST'])


def get_annotation_similarity_model_token(user_token: str, document_ids: List = None):
    if document_ids is not None:
        return user_token + '-' + sha256(str(sorted(document_ids)).encode('utf-8')).hexdigest() \
               + '-annotation_similarity_model_state'
    else:
        return user_token + '-annotation_similarity_model_state'


@_endpoint_route('/annotations/get-annotations')
@respond_with_json
@list_response
@list_annotation_ids
@list_document_ids
@list_pages
@requires_auth
def _get_annotations(request, number_of_items=30, offset=0, annotation_ids=None, document_ids=None, pages=None):
    search_term = optional_parameter(request, 'searchTerm', None)
    annotations = AnnotationStore.get_annotations(request['user'].token, search_term, annotation_ids, document_ids,
                                                  pages, saved_replies=False)
    return {'totalItems': len(annotations), 'items': annotations[offset:offset + number_of_items]}


@_endpoint_route('/annotations/add-annotation')
@respond_with_json
@dict_metadata
@requires_auth
def _add_annotation(request, metadata=None):
    question = required_parameter(request, 'question')
    answer = required_parameter(request, 'answer')
    document_id = required_parameter(request, 'documentId')
    page = optional_parameter(request, 'page', None)
    start_offset = optional_parameter(request, 'startOffset', None)
    end_offset = optional_parameter(request, 'endOffset', None)
    if start_offset is None or end_offset is None:
        raise UserException(ERROR_ANNOTATION_MISSING_PARAMS)
    if metadata is None:
        metadata = {}

    metadata['startOffset'] = int(start_offset)
    metadata['endOffset'] = int(end_offset)

    return AnnotationStore.create_annotation(request['user'].token, question, answer,
                                             document_id, page, metadata)


@_endpoint_route('/annotations/delete-annotation')
@respond_with_json
@requires_auth
def _delete_annotation(request):
    annotation_id = required_parameter(request, 'annotationId')
    return AnnotationStore.delete_annotation(request['user'].token, annotation_id)


@_endpoint_route('/annotations/edit-canonical-question')
@respond_with_json
@requires_auth
def _edit_canonical_question(request):
    annotation_id = required_parameter(request, 'annotationId')
    question = required_parameter(request, 'question')
    return AnnotationStore.edit_canonical_question(request['user'].token, annotation_id, question)


@_endpoint_route('/annotations/add-paraphrase-question')
@respond_with_json
@requires_auth
def _add_paraphrase_question(request):
    annotation_id = required_parameter(request, 'annotationId')
    question = required_parameter(request, 'question')
    return AnnotationStore.add_paraphrase_question(request['user'].token, annotation_id, question)


@_endpoint_route('/annotations/edit-paraphrase-question')
@respond_with_json
@requires_auth
def _edit_paraphrase_question(request):
    question_id = required_parameter(request, 'questionId')
    question = required_parameter(request, 'question')
    return AnnotationStore.edit_paraphrase_question(request['user'].token, question_id, question)


@_endpoint_route('/annotations/delete-paraphrase-question')
@respond_with_json
@requires_auth
def _delete_paraphrase_question(request):
    question_id = required_parameter(request, 'questionId')
    return AnnotationStore.delete_paraphrase_question(request['user'].token, question_id)


@_endpoint_route('/annotations/add-answer')
@respond_with_json
@requires_auth
def _add_answer(request):
    annotation_id = required_parameter(request, 'annotationId')
    answer = required_parameter(request, 'answer')
    return AnnotationStore.add_answer(request['user'].token, annotation_id, answer)


@_endpoint_route('/annotations/edit-answer')
@respond_with_json
@requires_auth
def _edit_answer(request):
    answer_id = required_parameter(request, 'answerId')
    answer = required_parameter(request, 'answer')
    return AnnotationStore.edit_answer(request['user'].token, answer_id, answer)


@_endpoint_route('/annotations/delete-answer')
@respond_with_json
@requires_auth
def _delete_answer(request):
    answer_id = required_parameter(request, 'answerId')
    return AnnotationStore.delete_answer(request['user'].token, answer_id)
