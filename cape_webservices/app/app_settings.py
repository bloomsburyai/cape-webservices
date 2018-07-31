from sanic import Blueprint

API_VERSION = '0.1'
URL_BASE = '/api/' + API_VERSION

app_endpoints = Blueprint('app_endpoints')
app_annotation_endpoints = Blueprint('app_annotation_endpoints')
app_document_endpoints = Blueprint('app_document_endpoints')
app_saved_reply_endpoints = Blueprint('app_saved_reply_endpoints')
app_inbox_endpoints = Blueprint('app_inbox_endpoints')
app_user_endpoints = Blueprint('app_user_endpoints')
app_email_endpoints = Blueprint('app_email_endpoints')
