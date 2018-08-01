from hashlib import sha256

from cape_webservices.app.app_settings import URL_BASE
from cape_webservices.app.app_settings import app_document_endpoints

from cape_document_manager.document_store import DocumentStore

from cape_webservices.app.app_middleware import respond_with_json, requires_auth
from cape_api_helpers.exceptions import UserException
from cape_api_helpers.output import list_response
from cape_api_helpers.input import required_parameter, optional_parameter, list_document_ids
from cape_api_helpers.text_responses import *
from cape_responder.responder_core import Responder

_endpoint_route = lambda x: app_document_endpoints.route(URL_BASE + x, methods=['GET', 'POST'])


@_endpoint_route('/documents/add-document')
@respond_with_json
@requires_auth
def _upload_document(request):
    user_token = request['user'].token
    title = required_parameter(request, 'title')
    if 'text' in request['args']:
        document_content = request['args']['text']
        document_type = 'text'
    elif 'file' in request.files:
        document_file = request.files.get('file')
        document_content = document_file.body.decode()
        document_type = 'file'
    else:
        raise UserException(ERROR_REQUIRED_PARAMETER % "text' or 'file")

    if 'documentid' in request['args'] and request['args']['documentid'] != '':
        document_id = request['args']['documentid']
    else:
        document_id = sha256(document_content.encode('utf-8')).hexdigest()

    if 'origin' in request['args'] and request['args']['origin'] != '':
        origin = request['args']['origin']
    else:
        origin = ''

    document_type = optional_parameter(request, 'type', document_type)
    replace = 'replace' in request['args'] and request['args']['replace'].lower() == 'true'

    DocumentStore.create_document(user_id=user_token,
                                  document_id=document_id,
                                  title=title,
                                  text=document_content,
                                  origin=origin,
                                  document_type=document_type,
                                  replace=replace,
                                  get_embedding=Responder.get_document_embeddings)

    return {'documentId': document_id}


@_endpoint_route('/documents/get-documents')
@respond_with_json
@list_response
@list_document_ids
@requires_auth
def _get_documents(request, number_of_items=30, offset=0, document_ids=None):
    user_token = request['user'].token
    search_term = optional_parameter(request, 'searchTerm', None)
    documents = DocumentStore.get_documents(user_token, document_ids=document_ids, search_term=search_term)
    return {'totalItems': len(documents), 'items': documents[offset:offset + number_of_items]}


@_endpoint_route('/documents/delete-document')
@respond_with_json
@requires_auth
def _delete_document(request):
    user_token = request['user'].token
    document_id = required_parameter(request, 'documentId')
    DocumentStore.delete_document(user_token, document_id)
    return {'documentId': document_id}


if __name__ == '__main__':
    pass
