import numbers

from pankoff.base import BaseValidator
from pankoff.exceptions import ValidationError

UNSET = object()


class Sized(BaseValidator):
    """
    Validate whether field length is within specified range.

    :param min_size: minimum length for a field
    :type min_size: int, optional

    :param max_size: maximum length for a field
    :type max_size: int, optional
    """

    def __setup__(self, min_size=None, max_size=None):
        self.min_size = min_size
        self.max_size = max_size

    def validate(self, instance, value):
        if self.min_size is not None and len(value) < self.min_size:
            raise ValidationError(f"Attribute `{self.field_name}` length should be >= {self.min_size}")
        elif self.max_size is not None and len(value) > self.max_size:
            raise ValidationError(f"Attribute `{self.field_name}` length should be <= {self.max_size}")


class Type(BaseValidator):
    """
    Validate whether field is instance of at least one type in ``types``.
    """

    def __setup__(self, types):
        self.types = types

    def validate(self, instance, value):
        if not isinstance(value, self.types):
            types_names = ", ".join(type_.__name__ for type_ in self.types)
            raise ValidationError(
                f"Attribute `{self.field_name}` should be an instance of `{types_names}`"
            )


class String(Type):
    """
    Validate whether field is instance of type ``str``.
    """

    def __setup__(self, types=(str,)):
        Type.__setup__(self, types)


class Number(Type):
    """
    Validate whether field is an instance of type ``int`` and within specified range.

    :param min_value: minimum value for a field
    :type min_value: int, optional

    :param max_value: maximum value for a field
    :type max_value: int, optional
    """

    def __setup__(self, min_value=None, max_value=None, types=(numbers.Number,)):
        Type.__setup__(self, types)
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, instance, value):
        Type.validate(self, instance, value)
        if self.min_value is not None and value < self.min_value:
            raise ValidationError(f"Attribute `{self.field_name}` should be >= {self.min_value}")
        elif self.max_value is not None and value > self.max_value:
            raise ValidationError(f"Attribute `{self.field_name}` should be <= {self.max_value}")


class Predicate(BaseValidator):
    """
    Predicate is a bit more complex validator.
    Basically, it checks your field against specified condition in ``predicate``.

    ``predicate`` is a simple callable which should return either ``True`` or ``False``.
    It'll be called with current ``instance`` and ``value`` to validate: ``predicate(instance, value)``.

    If ``predicate`` returned ``False``, and ``default`` is set, ``instance`` and ``value`` will be propagated to
    ``default`` if ``default`` is callable, if it's not, ``default`` will be returned straight away.

    THe key feature of ``default`` is that it can "normalize" your value if it's invalid. See example below.

    :param predicate: function to call in order to validate value
    :type predicate: callable

    :param default: default value to use if ``predicate`` returned ``False``
    :type default: callable, any, optional
    """

    def __setup__(self, predicate, default=UNSET, error_message=None):
        self.predicate = predicate
        self.default = default
        self.error_message = error_message

    def validate(self, instance, value):
        is_valid = self.predicate(instance, value)
        if not is_valid:
            if self.default is not UNSET:
                return self.default(instance, value) if callable(self.default) else self.default
            error_message = self.error_message or "Predicate {predicate} failed for field: {field_name}"
            raise ValidationError(
                error_message.format(
                    predicate=self.predicate.__name__,
                    field_name=self.field_name,
                    value=value
                )
            )


class LazyLoad(BaseValidator):
    """
    Calculate an attribute based on other fields.

    :param factory: callable to calculate value for current field, accepts current instance
    """

    def __setup__(self, factory):
        self.factory = factory

    def validate(self, instance, value):
        if value is not UNSET:
            raise RuntimeError(f"`{self.field_name}` is a `LazyLoad` field, you're not allowed to set it directly")
        return self.factory(instance)
