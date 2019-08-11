import re

PATTERNS = {
    'phone': r"""^[+]*[(]{0,1}[0-9]{0,4}[)]{0,1}[-\s\./0-9]*$""",
    'email': r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])""",
}
REGEXPS = {name: re.compile(pattern) for name, pattern in PATTERNS.items()}


def required(instance, field, value, message=None):
    if not value:
        raise ValueError(message or f'{field} is required')


def phone_number(instance, field, value, message=None):
    if re.match(REGEXPS['phone'], value) is None:
        raise ValueError(message or f'{field} does not match the valid pattern.')


def email(instance, field, value, message=None):
    if re.match(REGEXPS['email'], value) is None:
        raise ValueError(message or f'{field} does not match the valid pattern.')
