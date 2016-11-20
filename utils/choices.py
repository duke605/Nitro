import re
from argparse import ArgumentTypeError


def user(server):

    def test(s):
        match = re.search('^<@!?(\d+?)>$', s) or re.search('^(\d+)$', s)

        # Checking if string was mention
        if not match:
            raise ArgumentTypeError('invalid value: {} (must be mention)'.format(s))

        u = server.get_member(match.group(1))

        # Checking if user found
        if not u:
            raise ArgumentTypeError('invalid user id: {} (user could not be found)'.format(match.group(1)))

        return u

    return test
