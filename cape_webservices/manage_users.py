from optparse import OptionParser

from logging import info
from cape_userdb.user import User
from cape_userdb.session import Session
from cape_userdb.event import Event
from cape_userdb.bot import Bot
from cape_userdb.coverage import Coverage
from cape_userdb.email_event import EmailEvent
from cape_api_helpers.exceptions import UserException
from cape_api_helpers.text_responses import *
from cape_document_manager.document_store import DocumentStore
from cape_document_manager.annotation_store import AnnotationStore

"""
Script to create, delete and reset buffer for users.
"""


def create_user(user_id, password='bla', third_party_info=None, **user_attributes):
    """Create user, depending on global settings this will be in production or info DB."""
    user = User(
        **{'user_id': user_id.lower(), 'password': password, 'third_party_info': third_party_info, **user_attributes})
    user.save()
    info("User %s created successfully, with token: %s", user_id, user.token)
    return user


def delete_all_user_data(user_id):
    """Delete user, depending on global settings this will be in production or info DB."""
    user = User.get('user_id', user_id)
    if user is None:
        raise UserException(ERROR_USER_DOES_NOT_EXIST % user_id)
    documents = DocumentStore.get_documents(user.token)
    for document in documents:
        DocumentStore.delete_document(documents['id'])
    saved_replies = AnnotationStore.get_annotations(user.token, saved_replies=True)
    for saved_reply in saved_replies:
        AnnotationStore.delete_annotation(user.token, saved_reply['id'])
    annotations = AnnotationStore.get_annotations(user.token, saved_replies=False)
    for annotation in annotations:
        AnnotationStore.delete_annotation(user.token, annotation['id'])

    user.delete_instance()
    info("User " + user_id + " data deleted successfully")
    info("Looking for session data")
    del_counter = 0
    sessions = Session.all('user_id', user_id)
    for session in sessions:
        session.delete_instance()
        del_counter += 1
    info("Deleted " + str(del_counter) + " sessions")
    del_counter = 0
    events = Event.all('user_id', user_id)
    for event in events:
        event.delete_instance()
        del_counter += 1
    info("Deleted " + str(del_counter) + " events")
    del_counter = 0
    bots = Bot.all('user_id', user_id)
    for bot in bots:
        bot.delete_instance()
        del_counter += 1
    info("Deleted " + str(del_counter) + " bots")
    del_counter = 0
    coverage_entries = Coverage.all('user_id', user_id)
    for coverage in coverage_entries:
        coverage.delete_instance()
        del_counter += 1
    info("Deleted " + str(del_counter) + " coveragae entries")
    del_counter = 0
    email_events = EmailEvent.all('user_id', user_id)
    for event in email_events:
        event.delete_instance()
        del_counter += 1
    info("Deleted " + str(del_counter) + " email events")


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-c", "--create", dest="create", help="Create a user", action="store_true")
    parser.add_option("-d", "--delete", dest="delete", help="Delete a user", action="store_true")

    (options, args) = parser.parse_args()
    if options.create:
        if len(args) not in {2, 3}:
            print("Usage: manage_users.py -c <username> <password> <token>")
        else:
            if len(args) > 2:
                extra = {'token': args[2]}
            else:
                extra = {}
            create_user(args[0], args[1], **extra)
    elif options.delete:
        if len(args) != 1:
            print("Usage: manage_users.py -d <username>")
        else:
            delete_all_user_data(args[0])
    else:
        parser.print_help()
