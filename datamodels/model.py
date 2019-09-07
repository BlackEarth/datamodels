import json, sys
import dataclasses
from .util import JSONEncoder
from . import validators


class Model:
    """
    Create a model that builds on dataclasses to provide:
    * automatic post-init
    * converters 
    * validators
    * input from data
    * output to data
    """

    @classmethod
    def from_data(cls, data, keys=None):
        """pull field values out of a data source, ignoring data that is not in the model"""
        if not keys:
            keys = cls.__dataclass_fields__.keys()
        return cls(**{key: data[key] for key in keys if key in data})

    def __post_init__(self):
        """cast the input field values to the declared type, and then run any declared converters"""
        for field in self.__dataclass_fields__:
            try:
                value = getattr(self, field)
                if value:
                    # if converters are specified, use those;
                    # otherwise, cast the value to the field_type
                    field_metadata = self.__dataclass_fields__[field].metadata
                    if 'converters' in field_metadata:
                        for converter in field_metadata['converters']:
                            setattr(self, field, converter(value))
                    else:
                        field_type = self.__dataclass_fields__[field].type
                        # typing.List, etc. have __origin__ and __args__
                        if field_type.__dict__.get('__origin__'):
                            origin_type = field_type.__dict__['__origin__']
                            if field_type.__dict__.get('__args__'):
                                arg_types = field_type.__dict__['__args__']
                                if len(arg_types) == 1:
                                    setattr(self, field, origin_type(arg_types[0](value)))
                                else:
                                    setattr(
                                        self,
                                        field,
                                        origin_type(
                                            arg_types[i](value[i]) for i in range(len(arg_types))
                                        ),
                                    )
                            else:
                                setattr(self, field, origin_type(value))
                        else:
                            setattr(self, field, field_type(value))
            except ValueError as exc:
                if not exc.args:
                    exc.args = ('',)
                exc.args = (f'{self.__class__.__name__}.{field}: ' + ' '.join(exc.args),)
                raise

    def dict(self):
        return {k: v for k, v in dataclasses.asdict(self).items()}

    def json(self, indent=None):
        return json.dumps(self.dict(), indent=indent, cls=JSONEncoder)

    def keys(self):
        return self.dict().keys()

    def values(self):
        return iter([v for k, v in self.dict().items()])

    def items(self):
        return self.dict().items()

    def __iter__(self):
        for key in self.keys():
            yield key

    def is_valid(self):
        return not (bool(self.errors))

    def assert_valid(self):
        errors = self.errors
        if bool(errors) is True:
            raise ValueError("Validation failed: %s" % json.dumps(errors, indent=2))

    @property
    def pk(self):
        return {
            field: getattr(self, field)
            for field in self.__dataclass_fields__
            if self.__dataclass_fields__[field].metadata.get('pk')
        }

    @property
    def errors(self):
        """returns a dict of validation errors, keyed to attribute names"""
        validation_errors = {}
        for field in self.__class__.__dataclass_fields__:
            field_metadata = self.__dataclass_fields__[field].metadata
            if 'validators' in field_metadata:
                value = getattr(self, field)
                err = []
                for validator in field_metadata['validators']:
                    try:
                        validator(self, field, value)
                    except ValueError:
                        err.append(str(sys.exc_info()[1]))
                if len(err) > 0:
                    validation_errors[field] = err
        return validation_errors
