from datetime import date, datetime, time
import json
import re


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime) or isinstance(obj, date) or isinstance(obj, time):
            return str(obj)
        return super().default(obj)


class classproperty(property):
    def __get__(self, obj, objtype=None):
        return super(classproperty, self).__get__(objtype)

    def __set__(self, obj, value):
        super(classproperty, self).__set__(type(obj), value)

    def __delete__(self, obj):
        super(classproperty, self).__delete__(type(obj))


def nameify(string, ascii=False, sep='_'):
    """return an XML name (hyphen-separated by default, initial underscore if non-letter)"""
    s = camelsplit(string)  # immutable
    s = hyphenify(s, ascii=ascii).replace('-', sep)
    if len(s) == 0 or re.match("[A-Za-z_]", s[0]) is None:
        s = "_" + s
    return s


def camelsplit(string):
    """Turn a CamelCase string into a string with spaces"""
    s = str(string)
    for i in range(len(s) - 1, -1, -1):
        if i != 0 and (
            (s[i].isupper() and s[i - 1].isalnum() and not s[i - 1].isupper())
            or (s[i].isnumeric() and s[i - 1].isalpha())
        ):
            s = s[:i] + ' ' + s[i:]
    return s.strip()


def hyphenify(string, ascii=False):
    s = str(string)
    s = re.sub("""['"\u2018\u2019\u201c\u201d]""", '', s)  # quotes
    s = re.sub(r'(?:\s|%20)+', '-', s)  # whitespace
    if ascii == True:  # ASCII-only
        s = s.encode('ascii', 'xmlcharrefreplace').decode('ascii')  # use entities
    s = re.sub("&?([^;]*?);", r'.\1-', s)  # entities
    s = s.replace('#', 'u')
    s = re.sub(r"\W+", '-', s).strip(' -')
    return s
