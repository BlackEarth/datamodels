import json, sys
from dataclasses import asdict


class Model:
    PRIMARY_KEY = []
    VALIDATORS = {}

    @classmethod
    def from_data(cls, data):
        """pull field values out of a data source, ignoring data that is not in the model"""
        return cls(**{key: data[key] for key in cls.__dataclass_fields__ if key in data})

    def dict(self, empty=True):
        return {k: v for k, v in asdict(self).items() if bool(v) is True or empty is True}

    def json(self, empty=True, indent=None):
        return json.dumps(self.dict(empty=empty), indent=indent)

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

    @classmethod
    def add_validator(cls, field, validator):
        if field not in cls.VALIDATORS:
            cls.VALIDATORS[field] = []
            cls.VALIDATORS[field].append(validator)

