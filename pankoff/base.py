import functools
import inspect
from abc import ABCMeta, abstractmethod

from pankoff.combinator import combine

from pankoff.exceptions import ValidationError


# CAUTION!!! do not touch anything here


def _invalidate_call_cache(instance, target):
    instance_type = type(instance)
    for base in instance_type.mro():
        if hasattr(base, target):
            attribute = getattr(base, target, None)
            if hasattr(attribute, "__called__"):
                del attribute.__called__


class ExtendedABCMeta(ABCMeta):
    def __and__(cls, other):
        if getattr(cls, "__combinator__", False):
            bases = cls.__bases__
            bases += (other,)
            return combine(*bases)
        return combine(cls, other)


class _Descriptor:

    def __init__(self, **kwargs):
        _invalidate_call_cache(self, target="__setup__")

    def __set_name__(self, owner, name):
        self.field_name = name

    def __set__(self, instance, value, errors, **kwargs):
        _invalidate_call_cache(self, target="validate")
        if errors:
            raise ValidationError(errors)
        vars(instance)[self.field_name] = value


class BaseValidator(_Descriptor, metaclass=ExtendedABCMeta):

    def __init_subclass__(cls, **kwargs):
        def __cached_wrapper(func):
            @functools.wraps(func)
            def __inner(*args, **kw):
                __inner.__called__ = True
                ret = func(*args, **kw)
                return ret

            __inner.__wrapped__ = func
            return __inner

        for func_name in ("__setup__", "validate"):
            if hasattr(cls, func_name):
                setattr(cls, func_name, __cached_wrapper(getattr(cls, func_name)))

    def __init__(self, __mro__=None, **kwargs):
        kw = {}
        if not __mro__:
            __mro__ = type(self).mro()
        base, __mro__ = __mro__[0], __mro__[1:]

        signature = inspect.signature(base.__setup__)
        for parameter in signature.parameters.values():
            if parameter.name in kwargs:
                kw[parameter.name] = kwargs.pop(parameter.name)
        if base.__setup__ is not BaseValidator.__setup__:
            if not getattr(base.__setup__, "__called__", False):
                base.__setup__(self, **kw)
        super(base, self).__init__(__mro__=__mro__, **kwargs)

    def __set__(self, instance, value, __mro__=None, errors=None):
        errors = [] if errors is None else errors
        if not __mro__:
            __mro__ = type(self).mro()
        base, __mro__ = __mro__[0], __mro__[1:]
        if base.validate is not BaseValidator.validate:
            if not getattr(base.validate, "__called__", False):
                try:
                    base.validate(self, instance, value)
                except ValidationError as exc:
                    errors.append(str(exc))
        super(base, self).__set__(instance, value, __mro__=__mro__, errors=errors)

    def __setup__(self, *args, **kwargs):
        return NotImplemented

    @abstractmethod
    def validate(self, instance, value):
        return NotImplemented
