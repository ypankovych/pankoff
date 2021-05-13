import inspect
from abc import ABC, abstractmethod

from pankoff.exceptions import ValidationError


# CAUTION!!! do not touch anything here


def _was_not_initiated(instance, signature):
    for parameter in signature.parameters.values():
        if not hasattr(instance, parameter.name) and parameter.name != "self":
            return True
    return False


class _Descriptor:

    def __init__(self, **kwargs):
        del self._call_cache

    def __set_name__(self, owner, name):
        self.attr_name = name

    def __set__(self, instance, value, errors, **kwargs):
        del self._call_cache
        if errors:
            raise ValidationError(errors)
        vars(instance)[self.attr_name] = value


class BaseValidator(ABC, _Descriptor):

    def __init__(self, __mro__=None, **kwargs):
        kw = {}
        if not __mro__:
            __mro__ = type(self).mro()
        base, __mro__ = __mro__[0], __mro__[1:]
        if not hasattr(self, "_call_cache"):
            self._call_cache = set()

        signature = inspect.signature(base.__setup__)
        for parameter in signature.parameters.values():
            if parameter.name in kwargs:
                kw[parameter.name] = kwargs.pop(parameter.name)

        if id(base.__setup__) not in self._call_cache and _was_not_initiated(self, signature):
            base.__setup__(self, **kw)
            self._call_cache.add(id(base.__setup__))
        super(base, self).__init__(__mro__=__mro__, **kwargs)

    def __set__(self, instance, value, __mro__=None, errors=None):
        errors = [] if errors is None else errors
        if not __mro__:
            __mro__ = type(self).mro()
        base, __mro__ = __mro__[0], __mro__[1:]
        if not hasattr(self, "_call_cache"):
            self._call_cache = set()

        if id(base.validate) not in self._call_cache:
            try:
                base.validate(self, instance, value)
            except Exception as exc:
                errors.append(str(exc))
            self._call_cache.add(id(base.validate))
        super(base, self).__set__(instance, value, __mro__=__mro__, errors=errors)

    def __setup__(self, *args, **kwargs):
        return NotImplemented

    @abstractmethod
    def validate(self, instance, value):
        return NotImplemented
