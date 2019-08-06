import json, sys
from dataclasses import asdict
from .util import JSONEncoder


class Model:
    """
    Create a model that builds on @dataclasses.dataclass to provide:
    * automatic post-init
    * converters 
    * validators
    * input
    * output
    """
    CONVERTERS = {}
    VALIDATORS = {}

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
                    if field in self.CONVERTERS:
                        for converter in self.CONVERTERS[field]:
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
                                        self, field,
                                        origin_type(
                                            arg_types[i](value[i]) for i in range(len(arg_types))))
                            else:
                                setattr(self, field, origin_type(value))
                        else:
                            setattr(self, field, field_type(value))
            except ValueError as exc:
                if not exc.args:
                    exc.args = ('',)
                exc.args = (f'{self.__class__.__name__}.{field}: ' + ' '.join(exc.args),)
                raise

    def dict(self, empty=False):
        return {k: v for k, v in asdict(self).items() if empty is True or bool(v) is True}

    def json(self, empty=False, indent=None):
        return json.dumps(self.dict(empty=empty), indent=indent, cls=JSONEncoder)

    def keys(self, empty=False):
        return self.dict(empty=empty).keys()

    def values(self, empty=False):
        return iter([v for k, v in self.dict(empty=empty).items()])

    def items(self, empty=False):
        return self.dict(empty=empty).items()

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
