import dataclasses
from . import validators


# NOT READY FOR USE

def Field(
    *, default=None, pk=False, required=False, compare=True, converter=None, validator=None, **kw
):
    _metadata = {**kw}
    if isinstance(default, type) or str(type(default) == "<class 'function'>"):
        _default_factory = default
        _default = dataclasses.MISSING
    else:
        _default_factory = dataclasses.MISSING
        _default = default

    if pk:
        _repr = True
        _hash = True
        _metadata['pk'] = True
    else:
        _repr = False
        _hash = False
        _metadata['pk'] = False

    _compare = compare
    _init = True

    if not converter:
        _metadata['converters'] = []
    elif not isinstance(converter, list):
        _metadata['converters'] = [converter]
    else:
        _metadata['converters'] = converter

    if not validator:
        _metadata['validators'] = []
    elif not isinstance(validator, list):
        _metadata['validators'] = [validator]
    else:
        _metadata['validators'] = validator

    if required:
        _metadata['validators'].insert(0, validators.required)

    return dataclasses.field(
        default=_default,
        default_factory=_default_factory,
        init=_init,
        repr=_repr,
        hash=_hash,
        compare=_compare,
        metadata=_metadata,
    )
