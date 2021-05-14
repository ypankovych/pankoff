def combine(*validators, **kwargs):
    """
    Returns a combination of validators. E.g
    >>> name_validator = combine(Type, Sized)
    >>> name_validator(types=(str,), min_size=10)
    Of alternativelly:
    >>> name_validator = combine(Type, Sized, types=(str,), min_size=10)
    """
    from pankoff.base import ExtendedABCMeta

    def __repr__(self):
        validator_names = ", ".join(validator.__name__ for validator in type(self).__bases__)
        return f"{type(self).__name__}({validator_names})"
    klass = ExtendedABCMeta(
        "CombinedValidator",
        validators,
        {"__repr__": __repr__}
    )
    klass._validators = klass.__bases__
    klass.__combinator__ = True
    if not kwargs:
        return klass
    return klass(**kwargs)
