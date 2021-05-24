import functools
import inspect
import json
from abc import ABCMeta, abstractmethod
from types import MappingProxyType

from pankoff.combinator import combine
from pankoff.exceptions import ValidationError

# CAUTION!!! do not touch anything here

UNSET = object()


def is_combinator(obj):
    return getattr(obj, "__combinator__", False)


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

    def __iter__(self):
        return iter(self.asdict().items())

    @classmethod
    def extra(cls, **kwargs):
        """
        Add extra setup for your class future instances.
        This way you can create "temporary" objects, a.k.a factories.

        >>> fast_person = Person.extra(walk_speed=150)
        >>> slow_person = Person.extra(walk_speed=10)

        >>> yaroslav = fast_person(...)
        >>> john = slow_person(...)

        >>> print(yaroslav.walk_speed)  # 150
        >>> print(john.walk_speed)  # 10

        NOTE: extra args set at very beginning of instance setup, before any ``__init__``/etc

        See example: :ref:`Making factories`

        :param kwargs: arguments to set on instancee before ``__init__`` call
        """

        class _ExtraMeta(type):
            def __call__(cls, *args, **kw):
                instance = cls.__new__(cls, *args, **kw)
                instance._extra = MappingProxyType(kwargs)
                instance.__init__(*args, **kw)
                return instance

        return _ExtraMeta(cls.__name__, (cls,), dict(vars(cls)))

    def get_extra(self, key, default=UNSET):
        try:
            return self._extra[key]
        except KeyError:
            if default is not UNSET:
                return default
            raise

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
        :param data: data to validate
        :type data: dict

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

    def asdict(self, /, dump_aliases=False):
        """
        Dump your object do a dict. Dumps only validator fields and aliases.

        :param obj: object to dump
        :param dump_aliases: if ``True``, dump alias fields as well, defaults to ``False``

        :type dump_aliases: bool
        :return: dict

        >>> Person(...).asdict(dump_aliases=True)
        """
        ret = {}
        obj_type = type(self)
        bases = (BaseValidator,)
        if dump_aliases:
            from pankoff.magic import Alias
            bases += (Alias,)
        for name, field in vars(obj_type).items():
            if isinstance(field, bases):
                ret[name] = getattr(self, name)
        return ret

    def dumps(self, dumps, dump_aliases=False, **kwargs):
        """
        Dump current object using provided dumper, e.g ``yaml.dump`` or ``json.dumps``.

        :param dumps: callable to use on dump, defaults to ``json.dumps``
        :param dump_aliases: if ``True``, dump alias fields as well, defaults to ``False``
        :param kwargs: keyword arguments will be propagated to ``dumps``

        >>> Person.dumps(yaml.dump, dump_aliases=True)
        """
        return dumps(self.asdict(dump_aliases), **kwargs)

    def asjson(self, /, dump_aliases=False, **kwargs):
        """
        Same as ``asdict``, but returns JSON string.

        :param dump_aliases: if ``True``, dump alias fields as well, defaults to ``False``
        :param kwargs: keyword arguments will be propagated to ``dumps``
        :return: JSON string

        >>> Person(...).asjson(dump_aliases=True, indent=4)
        """
        return self.dumps(dump_aliases=dump_aliases, dumps=json.dumps, **kwargs)

    def asyaml(self, /, dump_aliases=False, **kwargs):
        """
        Dump object to YAML. Works only if PyYAML is installed.

        :param dump_aliases: if ``True``, dump alias fields as well, defaults to ``False``
        :param kwargs: keyword arguments will be propagated to ``dumps``
        :return: YAML string

        >>> Person.asyaml(dump_aliases=True)
        """
        try:
            import yaml
        except ImportError as exc:
            raise RuntimeError(
                "You should have https://pypi.org/project/PyYAML/ installed in order to do this action"
            ) from exc
        return self.dumps(dump_aliases=dump_aliases, dumps=yaml.dump, **kwargs)

    def to_path(self, /, path, dump_aliases=False, dumps=json.dumps, **kwargs):
        """
        Dump current instance to a file.
        :param path: path to dump to
        :type path: str

        :param dump_aliases: if ``True``, dump alias fields as well, defaults to ``False``
        :param dumps: callable to use on dump, defaults to ``json.dumps``
        :param kwargs: keyword arguments will be propagated to ``dumps``

        >>> Person(...).to_path("path/to/data.json", dump_aliases=True, indent=4)
        """
        with open(path, "w") as fp:
            fp.write(self.dumps(dump_aliases=dump_aliases, dumps=dumps, **kwargs))


def _invalidate_call_cache(instance, target):
    instance_type = type(instance)
    for base in instance_type.mro():
        if hasattr(base, target):
            attribute = getattr(base, target, None)
            if hasattr(attribute, "__called__"):
                del attribute.__called__


class ExtendedABCMeta(ABCMeta):
    def __and__(self, other):
        if is_combinator(self):
            bases = self.__bases__
            bases += (other,)
            return combine(*bases)
        return combine(self, other)

    def __repr__(self):
        if is_combinator(self):
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

    def __get__(self, instance, owner, __mro__, value):
        _invalidate_call_cache(self, target="mutate")
        return value


class BaseValidator(_Descriptor, metaclass=ExtendedABCMeta):

    def __init_subclass__(cls, **kwargs):
        """
        Wrap all required methods into cache wrappers to prevent duplicate invocations.
        """

        def __cached_wrapper(func):
            @functools.wraps(func)
            def __inner(*args, **kw):
                __inner.__called__ = True
                ret = func(*args, **kw)
                return ret

            __inner.__wrapped__ = func
            return __inner

        for func_name in ("__setup__", "validate", "mutate"):
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

    def __get__(self, instance, owner, __mro__=None, value=UNSET):
        """
        Call entire chain of mutators and propagate value to each of them.
        E.g: mutate(mutate(mutate(value))) and so on.
        """
        value = vars(instance)[self.field_name] if value is UNSET else value
        if not __mro__:
            __mro__ = type(self).mro()
        base, __mro__ = __mro__[0], __mro__[1:]
        if not getattr(base.mutate, "__called__", False):
            try:
                ret = base.mutate(self, instance, value)
                if ret is not NotImplemented:
                    value = ret
            except Exception:
                _invalidate_call_cache(self, target="mutate")
                raise
        return super(base, self).__get__(instance, owner, __mro__=__mro__, value=value)

    def __setup__(self, *args, **kwargs):
        return NotImplemented

    @abstractmethod
    def validate(self, instance, value):
        return NotImplemented

    def mutate(self, instance, value):
        return NotImplemented
