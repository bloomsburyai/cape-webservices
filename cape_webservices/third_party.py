from optparse import OptionParser
from cape_userdb.user import User

"""
Script to create, delete and reset buffer for users.
"""


def third_party(user_id):
    """Delete user, depending on global settings this will be in production or debug DB."""
    user = User.get('user_id', user_id)
    if user is None:
        print("User not found")
        return
    print(user.third_party_info['email'])


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-u", "--user", dest="user", help="Look up third party info for a user", action="store_true")

    (options, args) = parser.parse_args()
    if options.user:
        if len(args) != 1:
            print("Usage: manage_users.py -u <username>")
        else:
            third_party(args[0])
    else:
        parser.print_help()
