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


def between(low, high, inclusive=False):
    """
    Tests if a number is between 2 given values

    :param low: The lowest number the input can be
    :param high: The highest number the input can be
    :param inclusive: Makes the highest inclusive
    """

    def test(s):
        s = int(s)

        # Testing min value
        if s < low or s > high or (s >= high and not inclusive):

            if inclusive:
                raise ArgumentTypeError('invalid value: {} (must be between {:,} and {:,})'.format(s, low, high))
            else:
                raise ArgumentTypeError('invalid value: {} (must be between {:,} and {:,})'.format(s, low, high - 1))

        return s

    return test


def enum(options: dict):
    """
    Converts input into options

    :param options: The input allowed
    """

    def test(s):
        s = s.lower()

        for option in options:

            # Checking if the key matches the input
            if option.lower() == s:
                return option

            # Checking if the key has aliases
            if options[option] is None:
                continue

            # Checking if aliases are equal to the input
            for alias in options[option]:
                if alias.lower() == s:
                    return option

    return test
