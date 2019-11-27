import json, sys
import dataclasses
from .util import classproperty, JSONEncoder


class Model:
    """
    A model for data that builds on dataclasses to provide:
    
    * CONVERTERS – automatic post-init input field CONVERTERS
    * VALIDATORS – field validators, exposed via the .errors property
    * .load() – input from data
    * .dict() – output to data

    Any data model inherits from Model and includes the dataclass declaration form. 

    Example: Person model that converts a birthdate to a datetime, 
    and validates that the title, if given, is in {'Mr', 'Ms', 'Mrs', 'Dr'}:

    >>> from dataclasses import dataclass
    >>> from datetime import datetime, date
    >>> import dateparser  # pip install dateparser
    >>> from datamodels import Model  # pip install datamodels
    >>> 
    >>> @dataclass
    >>> class Person(Model):
    ...     ### use normal dataclass declaration forms for required and optional fields. 
    ...     name: str
    ...     title: str = None
    ...     birthdate: date = field(default=None)
    ... 
    ...     class CONVERTERS:
    ...         def birthdate(value):
    ...             return (
    ...                 dateparser.parse(value).date()
    ...                 if not isinstance(value, (datetime, date))
    ...                 else value
    ...             )
    ... 
    ...     class VALIDATORS:
    ...         def title(instance, field, value):
    ...             print(instance, field, value)
    ...             values = {'Mr', 'Ms', 'Mrs', 'Dr'}
    ...             if value is not None and value not in values:
    ...                 raise ValueError(f'{field} must be one of {values}.')
    ... 
    >>> person = Person(name='Joe', title='The', birthdate='Jan 20, 1990')
    >>> person.birthdate
    datetime.date(1990, 1, 20)
    >>> person.title
    'The'
    >>> person.errors
    {'title': ["title must be one of ['Mr', 'Ms', 'Mrs', 'Dr']."]}
    >>> 
    """

    CONVERTERS = object()
    VALIDATORS = object()

    @classproperty
    def FIELDS(cls):
        return cls.__dataclass_fields__

    @classmethod
    def load(cls, data, fields=None):
        """
        Load field values from data source, ignoring fields that are not in the model.
        """
        if not fields:
            fields = cls.__dataclass_fields__.keys()
        return cls(
            **{
                field: data[field]
                for field in list(fields)
                if field in data and field in cls.__dataclass_fields__
            }
        )

    def __post_init__(self):
        """
        Run any declared converters.
        """
        for field in self.__dataclass_fields__:
            value = getattr(self, field)
            if value:
                field_metadata = self.__dataclass_fields__[field].metadata
                if hasattr(self.CONVERTERS, field):
                    converter = getattr(self.CONVERTERS, field)
                    setattr(self, field, converter(value))

    def __iter__(self):
        for key in self.keys():
            yield key

    def dict(self, nulls=True):
        return {
            key: val
            for key, val in dataclasses.asdict(self).items()
            if nulls or val is not None
        }

    def json(self, nulls=True, encoder=None):
        if not encoder:
            encoder = JSONEncoder
        return json.dumps(self.dict(nulls=nulls), cls=encoder)

    def json_dict(self, nulls=True):
        """Provide a raw json-dump-able representation of the data."""
        return json.loads(self.json(nulls=nulls))

    def keys(self, nulls=True):
        return self.dict(nulls=nulls).keys()

    def values(self, nulls=True):
        return iter([v for k, v in self.dict(nulls=nulls).items()])

    def items(self, nulls=True):
        return self.dict(nulls=nulls).items()

    @property
    def errors(self):
        """returns a dict of validation errors, keyed to attribute names"""
        validation_errors = {}
        for field in self.__class__.__dataclass_fields__:
            if hasattr(self.VALIDATORS, field):
                validator = getattr(self.VALIDATORS, field)
                value = getattr(self, field)
                try:
                    validator(self, field, value)
                except ValueError:
                    validation_errors[field] = str(sys.exc_info()[1])

        return validation_errors

    def is_valid(self):
        return not (bool(self.errors))

    def assert_valid(self):
        errors = self.errors
        if bool(errors) is True:
            raise ValueError(
                "Validation failed: %s" % json.dumps(errors, cls=JSONEncoder)
            )
