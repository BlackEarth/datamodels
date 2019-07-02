import json, sys
from importlib import import_module
from dataclasses import dataclass, asdict
from .util import nameify, classproperty


class Model:
    CONVERTERS = {}
    VALIDATORS = {}
    SQL_DIALECT = None
    XML_NAMESPACE = None

    @classproperty
    def RELATION(cls):
        return nameify(cls.__name__).lower() + 's'

    @classproperty
    def PRIMARY_KEY(cls):
        """default primary key is a list with the first field name."""
        return list(cls.__dataclass_fields__.keys())[0:1]

    PK = PRIMARY_KEY

    @classmethod
    def from_data(cls, data):
        """pull field values out of a data source, ignoring data that is not in the model"""
        return cls(**{key: data[key] for key in cls.__dataclass_fields__ if key in data})

    def __post_init__(self):
        """cast the input field values to the declared type, and then run any declared converters"""
        for field in self.__dataclass_fields__:
            field_type = self.__dataclass_fields__[field].type
            try:
                value = getattr(self, field)
                if value and field in self.CONVERTERS:
                    for converter in self.CONVERTERS[field]:
                        setattr(self, field, converter(value))
            except ValueError as exc:
                if not exc.args:
                    exc.args = ('',)
                exc.args = (f'{self.__class__.__name__}.{field}: ' + ' '.join(exc.args),)
                raise

    def dict(self, empty=False):
        return {k: v for k, v in asdict(self).items() if bool(v) is True or empty is True}

    def json(self, empty=False, indent=None):
        return json.dumps(self.dict(empty=empty), indent=indent)

    def sql(self,
            query=None,
            fields=None,
            relation=None,
            keys=None,
            updates=None,
            dialect=None):
        SQL = import_module('sqlquery.sql').SQL
        return SQL(
            query=query or [],
            fields=fields or list(self.dict().keys()),
            relation=relation or self.RELATION,
            keys=keys or self.PRIMARY_KEY,
            updates=updates or self.nopk(),
            dialect=dialect or self.SQL_DIALECT)

    def keys(self):
        return [k for k in self.dict().keys()]

    def values(self):
        return [v for k, v in self.dict().items()]

    def items(self, empty=False):
        return self.dict(empty=empty).items()

    def __iter__(self):
        for key in self.keys():
            yield key

    def nopk(self):
        """data that are not part of the PRIMARY_KEY"""
        return {k: v for k, v in self.items() if k not in self.PK}

    def pk(self):
        """data in the PRIMARY_KEY"""
        return {k: v for k, v in self.items() if k in self.PK}

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
