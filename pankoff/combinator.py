from pankoff.exceptions import InconsistentOrderError


def combine(*validators, **kwargs):
    """
    Returns either "raw" combined validator or an instance of it.

    :param validators: Validators to combine
    :param kwargs: If specified, ``kwargs`` will be unpacked to newly created combined validator

    :returns: Either "raw" combined validator or its instance
    """
    from pankoff.base import ExtendedABCMeta

    def __repr__(self):
        validator_names = ", ".join(validator.__name__ for validator in type(self).__bases__)
        return f"{type(self).__name__}({validator_names})"

    try:
        klass = ExtendedABCMeta(
            "CombinedValidator",
            tuple(
                type(validator.__name__, (validator,), {})
                for validator in validators
            ),
            {"__repr__": __repr__}
        )
    except TypeError as exc:
        raise InconsistentOrderError(
            "Some validators either combined in a wrong order or cannot be combined together at all"
        ) from exc
    klass._validators = klass.__bases__
    klass.__combinator__ = True
    if not kwargs:
        return klass
    return klass(**kwargs)
