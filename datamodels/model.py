import json, sys
from importlib import import_module
from dataclasses import asdict
from .util import nameify, classproperty


class Model:
    SQL_DIALECT = None

    @classproperty
    def RELATION(cls):
        return nameify(cls.__name__).lower() + 's'

    @classproperty
    def PRIMARY_KEY(cls):
        """default primary key is a list with the first field name."""
        return list(cls.__dataclass_fields__.keys())[0:1]

    VALIDATORS = {}

    @classmethod
    def from_data(cls, data):
        """pull field values out of a data source, ignoring data that is not in the model"""
        return cls(**{key: data[key] for key in cls.__dataclass_fields__ if key in data})

    def dict(self, empty=True):
        return {k: v for k, v in asdict(self).items() if bool(v) is True or empty is True}

    def json(self, empty=True, indent=None):
        return json.dumps(self.dict(empty=empty), indent=indent)

    def sql(self, query=None, params=None, empty=True, pk=None, relation=None, dialect=None):
        SQL = import_module('sqlquery.sql').SQL
        return SQL(
            query=query or [],
            params=params or self.dict(empty=empty),
            pk=pk or self.PRIMARY_KEY,
            relation=relation or self.RELATION.lower() or self.__class__.__name__.lower() + 's',
            dialect=dialect or self.SQL_DIALECT)

    def keys(self):
        return (k for k in self.dict().keys())

    def values(self):
        return (v for k, v in self.dict().items())

    def items(self):
        return self.dict().items()

    def __iter__(self):
        return self.keys()

    def is_valid(self):
        return not (bool(self.errors()))

    def assert_valid(self):
        errors = self.errors()
        if bool(errors) is True:
            raise ValueError("Validation failed: %s" % json.dumps(errors, indent=2))

    def errors(self):
        """returns a dict of validation errors, keyed to attribute names"""
        validation_errors = {}
        for field in self.__class__.__dataclass_fields__:
            if field in self.VALIDATORS:
                value = self.__dict__[field]
                err = []
                for validator in self.VALIDATORS[field]:
                    try:
                        validator(self, field, value)
                    except ValueError:
                        err.append(str(sys.exc_info()[1]))
                if len(err) > 0:
                    validation_errors[field] = err
        return validation_errors
