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
import sys
import logging
from sanic.config import LOGGING

LOGGER = logging.getLogger('stream_logger')
HANDLER = 'logging.StreamHandler'
FORMATTER = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Remove file and syslog logging, handled from stdout
LOGGING['handlers'].pop('errorTimedRotatingFile', None)
LOGGING['handlers'].pop('accessTimedRotatingFile', None)
LOGGING['handlers'].pop('accessSysLog', None)
LOGGING['handlers'].pop('errorSysLog', None)

# Handled by the root logger
LOGGING['loggers'].pop('sanic', None)

LOGGING["formatters"]['stream_formatter'] = {
    'format': FORMATTER,
    'datefmt': '%Y-%m-%d %H:%M:%S',
}
LOGGING['handlers']['stream_handler'] = {
    'class': HANDLER,
    'formatter': 'stream_formatter',
    'stream': sys.stderr
}

LOGGING['loggers']['network']['handlers'] = ['accessStream']

LOGGING['root'] = {'level': os.environ.get("LOGLEVEL", "INFO").upper(),
                   'handlers': ['stream_handler']}


def envint(varname: str, default: int) -> int:
    return int(os.getenv(varname, default))


# SERVER configuration
CONFIG_SERVER = dict(
    host=os.getenv("CAPE_WEBSERVICE_HOST", "0.0.0.0"),
    port=envint("CAPE_WEBSERVICE_PORT", 5050), debug=True, workers=1, log_config=LOGGING,
)

# WEBAPP configuration
WEBAPP_CONFIG = dict(
    REQUEST_MAX_SIZE=envint("CAPE_WEBSERVICE_REQUEST_MAX_SIZE", int(100 * 1e6)),  # 100 megabytes
    REQUEST_TIMEOUT=envint("CAPE_WEBSERVICE_REQUEST_TIMEOUT", 600),  # 10 min
    KEEP_ALIVE=True,
    GRACEFUL_SHUTDOWN_TIMEOUT=envint("CAPE_WEBSERVICE_GRACEFUL_SHUTDOWN_TIMEOUT", 3),  # 3 sec
    WEBSOCKET_MAX_SIZE=envint("CAPE_WEBSERVICE_WEBSOCKET_MAX_SIZE", int(1e6)),  # 1 megabyte
    WEBSOCKET_MAX_QUEUE=envint("CAPE_WEBSERVICE_WEBSOCKET_MAX_QUEUE", 32)
)
MAX_NUMBER_OF_ANSWERS = envint("CAPE_WEBSERVICE_MAX_NUM_ANSWERS", 50)
HOSTNAME = os.getenv('CAPE_HOSTNAME', "DEV_SERVER")

# FILE configuration
THIS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__)))
STATIC_FOLDER = os.path.join(THIS_FOLDER, 'static')
HTML_INDEX_STATIC_FILE = os.path.join(STATIC_FOLDER, 'index.html')

MAX_SIZE_INLINE_TEXT = envint("CAPE_WEBSERVICE_MAX_SIZE_INLINE_TEXT", int(1.5e5))  # in number of characters

SUPER_ADMIN_TOKEN = "REPLACEME"

BOT_HELP_MESSAGE = """Hi, I am *Capebot*, I will answer all your questions, I will learn from you and your documents and improve over time.
Here are my commands:

    *.add* _question_ | _answer_ - Create a new saved reply.
    *.next* - Show the next possible answer for the last question.
    *.why* - Explain why the last answer was given.
    *.help* - Display this message.

You can also :

    *Ask* me to calculate, for example `what is 3+2?`.

For more options login to your account."""

ERROR_HELP_MESSAGE = "\n *Capebot* error type `.help` for more options."
