import functools
import inspect
import json
from abc import ABCMeta, abstractmethod

from pankoff.combinator import combine
from pankoff.exceptions import ValidationError


# CAUTION!!! do not touch anything here


class Container:

    def __repr__(self):
        """
        Make human readable representation of current instance.
        """
        field_names = ", ".join(
            f"{field.field_name}={getattr(self, field.field_name)}"
            for field in vars(type(self)).values()
            if isinstance(field, BaseValidator)
        )
        return f"{type(self).__name__}({field_names})"

    @classmethod
    def from_dict(cls, data):
        """
        Make on object from dictionary.

        :param data: dictionary to load
        :type data: dict
        """
        return cls(**data)

    @classmethod
    def from_json(cls, data, loader=json.loads):
        """
        Loads JSON and returns validated instance of it.
        """
        return cls.from_dict(loader(data))

    @classmethod
    def is_valid(cls, data):
        """
        Validate data
        :param data:
        :return: ``True/False``
        """
        try:
            cls.validate(data)
            return True
        except ValidationError:
            return False

    @classmethod
    def from_file(cls, fp, loader=json.load):
        """
        Loads content from file using ``loader`` and returns validated instance of it.

        :param fp: file object
        :param loader: defaults to ``json.load``
        """
        return cls.from_dict(loader(fp))

    @classmethod
    def from_path(cls, path, loader=json.load):
        """
        Reads file at given path and returns validates instance of it.
        Uses ``loader`` to load it.

        :param path: file path
        :param loader: defaults to ``json.load``
        """
        with open(path) as fp:
            return cls.from_file(fp, loader=loader)

    @classmethod
    def validate(cls, data):
        """
        Validate data and raise if its invalid.

        :param data: data to validate
        :type data: dict

        :raises: ValidationError
        """
        return cls.from_dict(data)


def _invalidate_call_cache(instance, target):
    instance_type = type(instance)
    for base in instance_type.mro():
        if hasattr(base, target):
            attribute = getattr(base, target, None)
            if hasattr(attribute, "__called__"):
                del attribute.__called__


class ExtendedABCMeta(ABCMeta):
    def __and__(self, other):
        if getattr(self, "__combinator__", False):
            bases = self.__bases__
            bases += (other,)
            return combine(*bases)
        return combine(self, other)

    def __repr__(self):
        if getattr(self, "__combinator__", False):
            validator_names = ", ".join(v.__name__ for v in self._validators)
            return f"Combination of ({validator_names}) validators"
        return super(ExtendedABCMeta, self).__repr__()


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
                try:
                    base.__setup__(self, **kw)
                except Exception:
                    _invalidate_call_cache(self, target="__setup__")
                    raise
        super(base, self).__init__(__mro__=__mro__, **kwargs)

    def __set__(self, instance, value, __mro__=None, errors=None):
        errors = [] if errors is None else errors
        if not __mro__:
            __mro__ = type(self).mro()
        base, __mro__ = __mro__[0], __mro__[1:]
        if base.validate is not BaseValidator.validate:
            if not getattr(base.validate, "__called__", False):
                try:
                    ret = base.validate(self, instance, value)
                    if ret is not None:
                        value = ret
                except ValidationError as exc:
                    errors.append(str(exc))
                except Exception:
                    _invalidate_call_cache(self, target="validate")
                    raise
        super(base, self).__set__(instance, value, __mro__=__mro__, errors=errors)

    def __get__(self, instance, owner):
        value = vars(instance)[self.field_name]
        mutated = self.mutate(instance, value)
        if mutated is NotImplemented:
            mutated = value
        return mutated

    def __setup__(self, *args, **kwargs):
        return NotImplemented

    @abstractmethod
    def validate(self, instance, value):
        return NotImplemented

    def mutate(self, instance, value):
        return NotImplemented
