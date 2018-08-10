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
