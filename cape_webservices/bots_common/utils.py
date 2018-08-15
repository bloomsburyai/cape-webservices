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

from typing import Optional, Tuple
from functools import wraps
from cape_webservices.app.app_core import _answer as responder_answer
from cape_webservices.webservices_settings import ERROR_HELP_MESSAGE, BOT_HELP_MESSAGE
from cape_webservices.app.app_saved_reply_endpoints import _create_saved_reply as responder_create_saved_reply
from cape_webservices.app.app_saved_reply_endpoints import _add_paraphrase_question as responder_add_paraphrase_question
from cape_api_helpers.text_responses import ERROR_FILE_TYPE_UNSUPPORTED
from cape_api_helpers.exceptions import UserException
from bs4 import BeautifulSoup
from markdown import markdown
from uuid import uuid4
import string
import json
import re
import math
import numexpr
import requests

# NON_WORD_CHARS.split('hola,ds.-com o_estas') ->['hola,ds.-com', 'o_estas']
NON_WORD_CHARS = re.compile('[\s]+')
# At which confidence search for a numerical expression?
NUMERICAL_EXPRESSION_THRESHOLD = 0.80
# from https://numexpr.readthedocs.io/en/latest/user_guide.html#supported-operators
NUMERICAL_EXPRESSION_STARTER = re.compile(
    '[%s]|' % re.escape(string.digits + '-(') + "|".join(
        ["exp", "where", "sin", "cos", "tan", "arcsin", "arccos", "arctan", "arctan2", "log", "sqrt", "abs", "conj",
         "real", "imag", "complex", "floor", "ceil"]))
NUMERICAL_EXPRESSION_ENDER = re.compile('[%s]' % re.escape(string.digits + ')'))

# Answer response to the last question asked, broken down by bot and channel
_previous_answers = {}
# Index of the last answer provided from _previous_answers, broken down by bot and channel
_last_answer = {}
# Echo mode
_ECHO_MODE = {}

_LAST_QUESTION = {}


def _process_responder_api(api_endpoint, request) -> Optional[dict]:
    response = json.loads(api_endpoint(request).body)
    if response['success']:
        return response
    else:
        raise UserException(response['result']['message'])


def try_numerical_answer(question: str) -> Optional[Tuple[str, str]]:
    if question.endswith('?') or question.endswith('.') or question.endswith('!'):
        question = question[:-1]
    words = NON_WORD_CHARS.split(question)
    starting_idx = None
    for idx, word in enumerate(words):
        if NUMERICAL_EXPRESSION_STARTER.match(word):
            starting_idx = idx
            break
    if starting_idx is None:
        return
    words = words[starting_idx:]
    length = len(words)
    ending_idx = None
    for idx, word in enumerate(reversed(words)):
        if NUMERICAL_EXPRESSION_ENDER.match("".join(reversed(word))):
            ending_idx = length - idx
            break
    expression = " ".join(words[:ending_idx])
    try:
        result = numexpr.evaluate(expression, local_dict={'pi': math.pi, 'tau': math.tau, 'e': math.e}, global_dict={})
    except Exception:
        return
    return expression, str(result)


def get_last_answer(comm_id):
    if comm_id not in _last_answer:
        return None
    return _previous_answers[comm_id][_last_answer[comm_id]]


def needs_question(wrapped):
    @wraps(wrapped)
    def decorated(user, comm_id, *args):
        if comm_id not in _last_answer:
            return {"text": "Please ask a question first."}
        else:
            return wrapped(user, comm_id, *args)

    return decorated


def _help(*args):
    return {"text": BOT_HELP_MESSAGE}


@needs_question
def _explain(user, comm_id, *args):
    previous = get_last_answer(comm_id)
    if previous['sourceType'] == 'document':
        context = previous["answerContext"]
        local_start_offset = previous['answerTextStartOffset'] - previous['answerContextStartOffset']
        local_end_offset = previous['answerTextEndOffset'] - previous['answerContextStartOffset']
        bold_text = context[local_start_offset:local_end_offset].replace('\n', '')
        context = f"{context[:local_start_offset]} *{bold_text}* {context[local_end_offset:]}"
        return {"text": f"From _{previous['sourceId']}_ (Index {previous['confidence']:.2f})\n>>>{context}"}
    else:
        return {
            "text": f"I thought you asked (Index {previous['confidence']:.2f})\n_{previous['matchedQuestion']}_\n>>>{previous['answerText']}"}


@needs_question
def _next(user, comm_id, *args):
    next_answer = _last_answer[comm_id] + 1
    if next_answer < len(_previous_answers[comm_id]):
        answer = _previous_answers[comm_id][next_answer]
        _last_answer[comm_id] = next_answer
        return {"text": answer['answerText']}
    else:
        return {"text": "I'm afraid I've run out of answers to that question."}


def _echo(user, space, request, message):
    if message.startswith(".echo"):
        _ECHO_MODE[space.space_id] = not _ECHO_MODE.get(space.space_id, False)
        return {"text": "Echo mode toggled"}
    else:
        return {"text": message}


def _add_saved_reply(user, comm_id, request, message):
    try:
        if message.startswith("."):
            message = message[NON_WORD_CHARS.search(message).end():]
        question_answer = [qa.strip() for qa in message.split('|')]
        if len(question_answer) < 2:
            raise IndexError()
    except IndexError:
        return {"text": "Sorry, I didn't understand that. The usage for `.add` is: .add question | answer"}

    request['user'] = user
    questions = question_answer[:-1]
    answer = question_answer[-1]
    request['args']['question'] = questions[0]
    request['args']['answer'] = answer
    response = _process_responder_api(responder_create_saved_reply, request)
    if not response:
        return
    reply_id = response['result']['replyId']
    for question in questions[1:]:
        request['args']['question'] = question
        request['args']['replyid'] = reply_id  # we do lower() for all parameters
        if not _process_responder_api(responder_add_paraphrase_question, request):
            return
    if len(questions) == 1:
        questions_text = f'_{questions[0]}_\n'
    else:
        questions_text = ''
        for question in questions:
            questions_text += f'•_{question}_\n'
    return {"text": f"Thanks, I'll remember that:\n{questions_text}>>>{answer}"}


def _answer(user, comm_id, request, question):
    request['args']['token'] = user.token
    request['args']['question'] = question
    request['args']['numberofitems'] = '5'
    try:
        response = _process_responder_api(responder_answer, request)
    except UserException as e:
        return {'text': e.message + ERROR_HELP_MESSAGE}
    if not response:
        return
    answers = response['result']['items']
    _previous_answers[comm_id] = answers
    _last_answer[comm_id] = 0
    _LAST_QUESTION[comm_id] = question
    if not answers or answers[0]['confidence'] < NUMERICAL_EXPRESSION_THRESHOLD:
        numerical_answer = try_numerical_answer(question)
        if numerical_answer:
            answers.insert(0, {"answerText": numerical_answer[0] + "=" + numerical_answer[1],
                               "confidence": 0.80,
                               "sourceType": "numerical",
                               "sourceId": str(uuid4()),
                               "matchedQuestion": f"What is {numerical_answer[0]} ?"
                               })
    if len(answers) == 0:
        return {"text": "Sorry! I don't know the answer to that."}
    else:
        return {"text": answers[0]['answerText']}


_ACTIONS = [
    (lambda user, comm_id, request, message: message.startswith(".echo") or _ECHO_MODE.get(comm_id, False),
     _echo),
    (lambda user, comm_id, request, message: message.startswith(".add"), _add_saved_reply),
    (lambda user, comm_id, request, message: "|" in message, _add_saved_reply),
    (lambda user, comm_id, request, message: message.startswith(".new"), _add_saved_reply),
    (lambda user, comm_id, request, message: message.startswith(".help"), _help),
    (lambda user, comm_id, request, message: message.startswith(".man"), _help),
    (lambda user, comm_id, request, message: message.startswith(".next"), _next),
    (lambda user, comm_id, request, message: message.startswith(".more"), _next),
    (lambda user, comm_id, request, message: message.startswith(".explain"), _explain),
    (lambda user, comm_id, request, message: message.startswith(".why"), _explain),
    (lambda user, comm_id, request, message: message.startswith(".context"), _explain),
    (lambda user, comm_id, request, message: message.startswith(".conf"), _explain),
    (lambda user, comm_id, request, message: message.startswith(".score"), _explain),
    (lambda user, comm_id, request, message: message.startswith(".index"), _explain),
    (lambda user, comm_id, request, message: True, _answer),
]


def process_action(user, comm_id, request, message):
    for checker, action in _ACTIONS:
        try:
            checked = checker(user, comm_id, request, message)
        except Exception:
            checked = False
        if checked:
            return action(user, comm_id, request, message)


def markdown_to_text(formatted_text):
    formatted_text = formatted_text.replace('  ', '&nbsp;&nbsp;')  # Preserve indentation
    formatted_text = re.sub('^$', '&nbsp;\n', formatted_text, flags=re.MULTILINE)  # Preserve blank lines
    html = markdown(formatted_text)
    return ''.join(BeautifulSoup(html, "html5lib").findAll(text=True))


def get_file_contents(url):
    file_request = requests.Session()
    response = file_request.get(url)
    print(response.headers)
    if not response.headers['Content-Type'].startswith('text/'):
        raise UserException(ERROR_FILE_TYPE_UNSUPPORTED)
    file_request.close()
    return response.text
