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

import os
from cape_webservices.app.app_settings import URL_BASE
from cape_webservices.app.app_settings import app_user_endpoints
from cape_userdb.cape_userdb_settings import DEFAULT_EMAIL

from cape_webservices.app.app_middleware import respond_with_json, requires_auth, requires_admin
from cape_userdb.user import User
from cape_userdb.event import Event
from cape_userdb.session import Session
from cape_userdb.coverage import Coverage
from cape_responder.responder_core import THRESHOLD_MAP
from cape_webservices.manage_users import create_user, delete_all_user_data
from cape_document_manager.annotation_store import AnnotationStore
from cape_document_manager.document_store import DocumentStore
from cape_api_helpers.exceptions import UserException
from cape_api_helpers.input import required_parameter, optional_parameter
from cape_api_helpers.text_responses import *
from peewee import IntegrityError

_endpoint_route = lambda x: app_user_endpoints.route(URL_BASE + x, methods=['GET', 'POST'])

AVAILABLE_PLANS = {'free', 'basic', 'pro'}


@_endpoint_route('/user/login')
@respond_with_json
def _login(request):
    login = required_parameter(request, 'login')
    password = required_parameter(request, 'password')
    user = User.get('user_id', login)
    if user is None or not user.verify_password(password):
        raise UserException(INVALID_CREDENTIALS_TEXT)
    session_obj: Session = Session.create(user_id=user.user_id)
    request['session_id'] = session_obj.session_id
    return {'message': VALID_CREDENTIALS_TEXT, 'sessionId': session_obj.session_id, 'adminToken': user.admin_token}


@_endpoint_route('/user/logout')
@respond_with_json
@requires_auth
def _logout(request):
    if 'user' in request:
        del request['user']
    if 'session_id' in request:
        del request['session_id']
    return {'message': LOGGED_OUT_TEXT}


@_endpoint_route('/user/get-user-token')
@respond_with_json
@requires_auth
def _get_user_token(request):
    return {'userToken': request['user'].token}


@_endpoint_route('/user/get-admin-token')
@respond_with_json
@requires_auth
def _get_admin_token(request):
    return {'adminToken': request['user'].admin_token}


@_endpoint_route('/user/get-default-threshold')
@respond_with_json
@requires_auth
def _get_default_threshold(request):
    return {'threshold': request['user'].document_threshold.lower()}


@_endpoint_route('/user/set-default-threshold')
@respond_with_json
@requires_auth
def _set_default_threshold(request):
    threshold = required_parameter(request, 'threshold').upper()
    if threshold not in THRESHOLD_MAP['document']:
        raise UserException(ERROR_INVALID_THRESHOLD)
    request['user'].document_threshold = threshold
    request['user'].saved_reply_threshold = threshold
    request['user'].save()
    return {'threshold': threshold.lower()}


@_endpoint_route('/user/set-plan')
@respond_with_json
@requires_auth
def _set_plan(request):
    plan = required_parameter(request, 'plan').lower()
    if plan not in AVAILABLE_PLANS:
        raise UserException(ERROR_INVALID_PLAN % (plan, str(AVAILABLE_PLANS)))
    request['user'].plan = plan
    request['user'].save()
    return {'plan': plan}


@_endpoint_route('/user/set-terms-agreed')
@respond_with_json
@requires_auth
def _set_agreed_terms(request):
    request['user'].terms_agreed = True
    request['user'].save()
    return {'termsAgreed': True}


@_endpoint_route('/user/set-onboarding-completed')
@respond_with_json
@requires_auth
def _set_onboarding_completed(request):
    request['user'].onboarding_completed = True
    request['user'].save()
    return {'onboardingCompleted': True}


@_endpoint_route('/user/get-profile')
@respond_with_json
@requires_auth
def _get_profile(request):
    forward_email = request['user'].forward_email
    if forward_email == DEFAULT_EMAIL:
        forward_email = None

    return {'username': request['user'].user_id, 'plan': request['user'].plan,
            'termsAgreed': request['user'].terms_agreed, 'onboardingCompleted': request['user'].onboarding_completed,
            'forwardEmail': forward_email, 'forwardEmailVerified': request['user'].forward_email_verified}


@_endpoint_route('/user/create-user')
@respond_with_json
@requires_admin
def _create_user(request):
    user_id = required_parameter(request, 'userId').lower()
    password = required_parameter(request, 'password')
    token = optional_parameter(request, 'token', None)
    admin_token = optional_parameter(request, 'adminToken', None)
    threshold = optional_parameter(request, 'threshold', None)
    terms_agreed = optional_parameter(request, 'termsAgreed', None)
    plan = optional_parameter(request, 'plan', None)

    try:
        user = create_user(user_id, password)
    except IntegrityError as e:
        raise UserException(e.args[1])

    if token:
        user.token = token
    if admin_token:
        user.admin_token = admin_token
    if threshold:
        threshold = threshold.lower()
        if threshold not in THRESHOLD_MAP['document']:
            raise UserException(ERROR_INVALID_THRESHOLD)
        user.document_threshold = threshold
        user.saved_reply_threshold = threshold
    if terms_agreed:
        terms_agreed = terms_agreed.lower()
        if terms_agreed == 'true':
            user.terms_agreed = True
        elif terms_agreed == 'false':
            user.terms_agreed = False
        else:
            raise UserException(ERROR_INVALID_TERMS % terms_agreed)
    if plan:
        plan = plan.lower()
        if plan in AVAILABLE_PLANS:
            user.plan = plan
        else:
            raise UserException(ERROR_INVALID_PLAN % (plan, str(AVAILABLE_PLANS)))

    user.save()

    return {'username': user.user_id}


@_endpoint_route('/user/delete-user')
@respond_with_json
@requires_admin
def _delete_user(request):
    user_id = required_parameter(request, 'userId').lower()
    delete_all_user_data(user_id)
    return {'username': user_id}



@_endpoint_route('/user/stats')
@respond_with_json
@requires_auth
def _stats(request):
    user_id = request['user'].user_id
    events = Event.select().where(Event.user_id == user_id).order_by(Event.created.desc())
    total = events.count()
    automatic = 0
    assisted = 0
    unanswered = 0
    total_duration = 0
    average_response_time = 0
    questions = []
    source_count = {}
    coverage = []

    # Find total number of saved replies
    total_saved_replies = len(AnnotationStore.get_annotations(request['user'].token, saved_replies=True))

    # Find total number of documents
    documents = DocumentStore.get_documents(request['user'].token)
    total_documents = len(documents)

    for event in events:
        question = {
            'created': event.created,
            'duration': event.duration,
            'question': event.question
        }
        if event.answered:
            answer = event.answers[0]
            total_duration += event.duration
            question['answer'] = answer['answerText']
            if answer['sourceType'] == 'saved_reply':
                automatic += 1
                question['status'] = 'automatic'
                question['matchedQuestion'] = answer['matchedQuestion']
            else:
                assisted += 1
                question['status'] = 'assisted'
                if answer['sourceId'] in source_count:
                    source_count[answer['sourceId']] += 1
                else:
                    source_count[answer['sourceId']] = 1
        else:
            unanswered += 1
            question['status'] = 'unanswered'
        questions.append(question)

    source_count['saved_reply'] = automatic
    source_count['unanswered'] = unanswered
    sources = sorted(source_count.items(), key=lambda x: x[1], reverse=True)
    sources_percent = []
    if total > 0:
        for source in sources:
            if source[0] == 'saved_reply':
                document_title = 'Saved replies'
            elif source[0] == 'unanswered':
                document_title = 'Unanswered'
            else:
                document_title = source[0]
                if source[0] in documents:
                    if documents:
                        if len(documents[source[0]]['title']) > 0:
                            document_title = documents[source[0]]['title']
                else:
                    document_title = 'Deleted document'
            sources_percent.append({'source': source[0], 'title': document_title, 'percent': (source[1] / total) * 100})
        average_response_time = total_duration / total

    coverage_stats = Coverage.select().where(Coverage.user_id == user_id)
    for stat in coverage_stats:
        coverage.append({'coverage': stat.coverage, 'time': stat.created})

    return {'averageResponseTime': average_response_time, 'totalSavedReplies': total_saved_replies,
            'totalDocuments': total_documents, 'totalQuestions': total, 'automatic': automatic, 'assisted': assisted,
            'unanswered': unanswered, 'sources': sources_percent, 'questions': questions, 'coverage': coverage}
