import functools

def validator(method):
    """Decorate a method with this to make it a field validator.
    """

    @functools.wraps(method)
    def make_validator(self, field):
        if field not in self.__class__.META.validators:
            self.__class__.META.validators = []
        self.__class__.META.validators.append(method)

        return method

    return make_validator()
