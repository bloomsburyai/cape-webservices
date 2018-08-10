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

from cape.client.exceptions import CapeException
from cape_webservices.tests.test_api.conftest import CapeClient, API_URL
import pytest, time


# pytest automatically imports cape_client fixture in conftest.py


def test_token(cape_client):
    token = cape_client.get_user_token()
    assert token


def test_admin_token(cape_client):
    admin_token = cape_client.get_admin_token()
    # Authenticate another client using the admin token
    cape_client2 = CapeClient(API_URL, admin_token)
    token = cape_client2.get_user_token()
    assert token == cape_client.get_user_token()


def test_saved_replies(cape_client):
    # Get Saved Replies
    saved_replies = cape_client.get_saved_replies()['items']

    # Delete all existing saved replies
    for saved_reply in saved_replies:
        cape_client.delete_saved_reply(saved_reply['id'])
    assert cape_client.get_saved_replies()['totalItems'] == 0

    # Create saved replies
    reply_id = cape_client.create_saved_reply(question='Question', answer='Answer')['replyId']
    cape_client.create_saved_reply(question='Another Question', answer='Another Answer')
    saved_replies = cape_client.get_saved_replies()['items']
    assert len(saved_replies) == 2

    # Check number_of_items and offset
    saved_replies = cape_client.get_saved_replies(number_of_items=1)['items']
    assert len(saved_replies) == 1
    saved_replies = cape_client.get_saved_replies(offset=1)['items']
    assert len(saved_replies) == 1

    # Search
    saved_replies = cape_client.get_saved_replies(search_term='another')
    assert saved_replies['totalItems'] == 1

    # Check searchReplyId
    specific_replies = cape_client.get_saved_replies(saved_reply_ids=[saved_replies['items'][0]['id']])
    assert specific_replies['items'][0]['id'] == saved_replies['items'][0]['id']

    # Add paraphrase questions
    paraphrase_id = cape_client.add_paraphrase_question(reply_id, question='Paraphrase Question')
    cape_client.add_paraphrase_question(reply_id, question='Another Paraphrase Question')
    cape_client.add_paraphrase_question(reply_id, question='Yet Another Paraphrase Question')
    for saved_reply in cape_client.get_saved_replies()['items']:
        if saved_reply['id'] == reply_id:
            assert len(saved_reply['paraphraseQuestions']) == 3
        else:
            assert len(saved_reply['paraphraseQuestions']) == 0

    # Modify paraphrase question
    modified_paraphrase_text = 'Modified Paraphrase Question'
    cape_client.edit_paraphrase_question(paraphrase_id, modified_paraphrase_text)
    saved_reply = \
        [saved_reply for saved_reply in cape_client.get_saved_replies()['items'] if saved_reply['id'] == reply_id][0]
    for paraphrase_question in saved_reply['paraphraseQuestions']:
        if paraphrase_question['id'] == paraphrase_id:
            assert paraphrase_question['question'] == modified_paraphrase_text
        else:
            assert paraphrase_question['question'] != modified_paraphrase_text

    # Delete paraphrase question
    cape_client.delete_paraphrase_question(paraphrase_id)
    for saved_reply in cape_client.get_saved_replies()['items']:
        if saved_reply['id'] == reply_id:
            assert len(saved_reply['paraphraseQuestions']) == 2
        else:
            assert len(saved_reply['paraphraseQuestions']) == 0

    # Modify the canonical question
    modified_canonical_question = 'Modified Canonical Question'
    cape_client.edit_canonical_question(reply_id, modified_canonical_question)
    saved_reply = \
        [saved_reply for saved_reply in cape_client.get_saved_replies()['items'] if saved_reply['id'] == reply_id][0]
    assert saved_reply['canonicalQuestion'] == modified_canonical_question

    # Add answers
    answer_id = cape_client.add_answer(reply_id, answer='Added Answer')
    cape_client.add_answer(reply_id, answer='Another Answer')
    cape_client.add_answer(reply_id, answer='Yet Another Answer')
    cape_client.add_answer(reply_id, answer='You guessed right, another answer')
    for saved_reply in cape_client.get_saved_replies()['items']:
        if saved_reply['id'] == reply_id:
            assert len(saved_reply['answers']) == 5
        else:
            assert len(saved_reply['answers']) == 1

    # Modify answer
    modified_answer_text = 'Modified Answer Text'
    cape_client.edit_answer(answer_id, modified_answer_text)
    saved_reply = \
        [saved_reply for saved_reply in cape_client.get_saved_replies()['items'] if saved_reply['id'] == reply_id][0]
    for answer in saved_reply['answers']:
        if answer['id'] == answer_id:
            assert answer['answer'] == modified_answer_text
        else:
            assert answer['answer'] != modified_answer_text

    # Delete answer
    cape_client.delete_answer(answer_id)
    for saved_reply in cape_client.get_saved_replies()['items']:
        if saved_reply['id'] == reply_id:
            assert len(saved_reply['answers']) == 4
        else:
            assert len(saved_reply['answers']) == 1

    # Try to delete an answer from a saved reply with only 1 answer
    reply_id = cape_client.create_saved_reply('New Question', 'New Answer')['replyId']
    saved_reply = \
        [saved_reply for saved_reply in cape_client.get_saved_replies()['items'] if saved_reply['id'] == reply_id][0]
    answer_id = saved_reply['answers'][0]['id']
    with pytest.raises(CapeException):
        cape_client.delete_answer(answer_id)
    saved_reply = \
        [saved_reply for saved_reply in cape_client.get_saved_replies()['items'] if saved_reply['id'] == reply_id][0]
    assert len(saved_reply['answers']) == 1


def test_annotations(cape_client):
    cape_client.add_annotation('Where is the cat?', 'On the mat', 'Animals', start_offset=12, end_offset=24)
    annotations = cape_client.get_annotations(search_term='cat')
    assert annotations['totalItems'] == 1

    response = cape_client.add_annotation('Where is the dog?', 'On the log', 'Animals', start_offset=34, end_offset=58)
    annotations = cape_client.get_annotations(annotation_ids=[response['annotationId']])
    assert annotations['totalItems'] == 1

    answers = cape_client.answer('Where is the dog?')
    assert answers[0]['answerText'] == 'On the log'
    assert answers[0]['sourceType'] == 'annotation'
    assert answers[0]['metadata']['startOffset'] == 34

    annotations = cape_client.get_annotations(document_ids=['Animals'])
    assert annotations['totalItems'] == 2

    answer_id = cape_client.add_annotation_answer(response['annotationId'], 'Another answer')
    annotations = cape_client.get_annotations(annotation_ids=[response['annotationId']])
    assert len(annotations['items'][0]['answers']) == 2

    cape_client.edit_annotation_answer(answer_id, 'Yet another answer')
    annotations = cape_client.get_annotations(annotation_ids=[response['annotationId']])
    assert annotations['items'][0]['answers'][1]['answer'] == 'Yet another answer'

    cape_client.delete_annotation_answer(answer_id)
    annotations = cape_client.get_annotations(annotation_ids=[response['annotationId']])
    assert len(annotations['items'][0]['answers']) == 1

    cape_client.edit_annotation_canonical_question(response['annotationId'], "New question?")
    annotations = cape_client.get_annotations(annotation_ids=[response['annotationId']])
    assert annotations['items'][0]['canonicalQuestion'] == "New question?"

    question_id = cape_client.add_annotation_paraphrase_question(response['annotationId'], "Another question?")
    annotations = cape_client.get_annotations(annotation_ids=[response['annotationId']])
    assert annotations['items'][0]['paraphraseQuestions'][0]['question'] == "Another question?"

    cape_client.edit_annotation_paraphrase_question(question_id, "Yet another question?")
    annotations = cape_client.get_annotations(annotation_ids=[response['annotationId']])
    assert annotations['items'][0]['paraphraseQuestions'][0]['question'] == "Yet another question?"

    cape_client.delete_annotation_paraphrase_question(question_id)
    annotations = cape_client.get_annotations(annotation_ids=[response['annotationId']])
    assert len(annotations['items'][0]['paraphraseQuestions']) == 0

    cape_client.delete_annotation(response['annotationId'])
    annotations = cape_client.get_annotations(document_ids=['Animals'])
    assert annotations['totalItems'] == 1

    cape_client.add_annotation('Where is the cat?', 'On my hat', 'Strange Animals', start_offset=12, end_offset=24)
    answers = cape_client.answer('Where is the cat?', document_ids=['Animals'])
    assert answers[0]['answerText'] == 'On the mat'
    answers = cape_client.answer('Where is the cat?', document_ids=['Strange Animals'])
    assert answers[0]['answerText'] == 'On my hat'

    cape_client.add_annotation('Does this have metadata?', 'Yes', 'Custom Stuff', start_offset=0, end_offset=3,
                               metadata={
                                   'custom_field': 'testing'
                               })
    answers = cape_client.answer('Does this have metadata?', document_ids=['Custom Stuff'])
    assert answers[0]['metadata']['custom_field'] == 'testing'

    for annotation in cape_client.get_annotations()['items']:
        cape_client.delete_annotation(annotation['id'])

    with pytest.raises(CapeException):
        cape_client.delete_annotation('fakeid')

    with pytest.raises(CapeException):
        cape_client.add_annotation_answer('fakeid', 'fake answer')

    with pytest.raises(CapeException):
        cape_client.delete_annotation_answer('fakeid')

    with pytest.raises(CapeException):
        cape_client.edit_annotation_answer('fakeid', 'fake answer')

    with pytest.raises(CapeException):
        cape_client.edit_annotation_canonical_question('fakeid', 'fake question')

    with pytest.raises(CapeException):
        cape_client.add_annotation_paraphrase_question('fakeid', 'fake question')

    with pytest.raises(CapeException):
        cape_client.edit_annotation_paraphrase_question('fakeid', 'fake question')

    with pytest.raises(CapeException):
        cape_client.delete_annotation_paraphrase_question('fakeid')

    with pytest.raises(CapeException):
        cape_client.add_annotation('Do we have both a start and end offset?', 'No', 'Failures', end_offset=43)

    with pytest.raises(CapeException):
        cape_client.add_annotation('Do we have both a start and end offset?', 'No', 'Failures', start_offset=12)


def test_invalid_delete_reply(cape_client):
    with pytest.raises(CapeException):
        cape_client.delete_saved_reply('fake')


def test_invalid_edit_canonical_question(cape_client):
    with pytest.raises(CapeException):
        cape_client.edit_canonical_question('fake', 'Test')


def test_invalid_add_paraphrase_question(cape_client):
    with pytest.raises(CapeException):
        cape_client.add_paraphrase_question('fake', 'Test')


def test_invalid_edit_paraphrase_question(cape_client):
    with pytest.raises(CapeException):
        cape_client.edit_paraphrase_question('fake', 'Test')


def test_invalid_delete_paraphrase_question(cape_client):
    with pytest.raises(CapeException):
        cape_client.delete_paraphrase_question('fake')


def test_invalid_add_answer(cape_client):
    with pytest.raises(CapeException):
        cape_client.add_answer('fake', 'Test')


def test_invalid_edit_answer(cape_client):
    with pytest.raises(CapeException):
        cape_client.edit_answer('fake', 'Test')


def test_documents(cape_client):
    cape_client.upload_document(title='Test', text='Testing', origin='A test', replace=True)
    documents = cape_client.get_documents()['items']
    assert len(documents) > 0
    for document in documents:
        cape_client.delete_document(document['id'])
    documents = cape_client.get_documents()['items']
    assert len(documents) == 0


def test_answer(cape_client):
    documents = cape_client.get_documents()['items']
    for document in documents:
        cape_client.delete_document(document['id'])
    cape_client.upload_document(title='Sky', text='The sky is blue.', origin='sky.txt', replace=True)
    answers = cape_client.answer('What colour is the sky?', source_type="document")
    assert answers[0]['answerText'] == 'blue'


def test_answer_inline(cape_client):
    documents = cape_client.get_documents()['items']
    for document in documents:
        cape_client.delete_document(document['id'])
    answers = cape_client.answer('What colour is the sky?', source_type="document", text="The sky is blue")
    assert answers[0]['answerText'] == 'blue'


def test_answer_from_saved_replies(cape_client_answer):
    cape_client = cape_client_answer

    print(cape_client.get_saved_replies()['totalItems'])
    cape_client.create_saved_reply(question='What is a dog?', answer='A dog is a pet')
    print(cape_client.get_saved_replies()['totalItems'])
    cape_client.create_saved_reply(question='What is a horse?', answer='A horse is a pet')
    print(cape_client.get_saved_replies()['totalItems'])
    cape_client.create_saved_reply(question='What is a cat?', answer='A cat is a pet')
    print(cape_client.get_saved_replies()['totalItems'])
    cape_client.create_saved_reply(question='What is a fish?', answer='A fish is a pet')
    print(cape_client.get_saved_replies()['totalItems'])
    cape_client.create_saved_reply(question='What is a potato?', answer='A potato is a vegetable')
    print(cape_client.get_saved_replies()['totalItems'])

    assert cape_client.get_saved_replies()['totalItems'] == 5

    # Answer
    answers = cape_client.answer('What is a fish?', source_type="saved_reply")
    assert answers[0]['answerText'] == 'A fish is a pet'


def test_inbox(cape_client):
    events = cape_client.get_inbox()['items']
    for event in events:
        cape_client.archive_inbox(event['id'])
    events = cape_client.get_inbox()['items']
    assert len(events) == 0
    cape_client.answer('What colour is the sky?')
    # HACK: Saving inbox events is sent to a worker and doesn't block, so we can't know for sure when it finishes
    time.sleep(1)
    events = cape_client.get_inbox()['items']
    item = events[0]
    assert len(events) == 1
    events = cape_client.get_inbox(read=True)['items']
    assert len(events) == 0
    cape_client.mark_inbox_read(item['id'])
    events = cape_client.get_inbox(read=True)['items']
    assert len(events) == 1
    cape_client.archive_inbox(item['id'])
    events = cape_client.get_inbox(read=True)['items']
    assert len(events) == 0


def test_default_threshold(cape_client):
    cape_client.set_default_threshold('high')
    threshold = cape_client.get_default_threshold()
    assert threshold == 'high'
    cape_client.set_default_threshold('medium')
    threshold = cape_client.get_default_threshold()
    assert threshold == 'medium'


def test_invalid_threshold(cape_client):
    with pytest.raises(CapeException):
        cape_client.set_default_threshold('potato')


def test_user_profile(cape_client):
    profile = cape_client.get_profile()
    assert profile == {'username': 'testuser', 'plan': 'free', 'termsAgreed': False, 'onboardingCompleted': False,
                       'forwardEmail': None,'forwardEmailVerified':False}


def test_spans(cape_client: CapeClient):
    for document in cape_client.get_documents()['items']:
        cape_client.delete_document(document['id'])
    for saved_reply in cape_client.get_saved_replies()['items']:
        cape_client.delete_saved_reply(saved_reply['id'])
    texts = {}
    texts['Pizza'] = 'I like pizzas.'
    texts['Sky'] = "The sky is blue."
    texts['Colour'] = "My favorite colour is red"
    questions = {"Do you like pizzas ?", "What is red?", "what is sky?"}
    for title, text in texts.items():
        cape_client.upload_document(title, text, document_id=title)
    for question in questions:
        answer = cape_client.answer(question)[0]
        assert answer['answerText'] in answer['answerContext']
        assert answer['answerText'] == texts[answer['sourceId']][
                                       answer['answerTextStartOffset']:answer['answerTextEndOffset']]
        assert answer['answerContext'] == texts[answer['sourceId']][
                                          answer['answerContextStartOffset']:answer['answerContextEndOffset']]
    for document in cape_client.get_documents()['items']:
        cape_client.delete_document(document['id'])
    for saved_reply in cape_client.get_saved_replies()['items']:
        cape_client.delete_saved_reply(saved_reply['id'])
