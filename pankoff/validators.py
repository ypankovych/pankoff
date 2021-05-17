import numbers

from pankoff.base import BaseValidator
from pankoff.exceptions import ValidationError

UNSET = object()


class Sized(BaseValidator):

    def __setup__(self, min_size=None, max_size=None):
        self.min_size = min_size
        self.max_size = max_size

    def validate(self, instance, value):
        if self.min_size is not None and len(value) < self.min_size:
            raise ValidationError(f"Attribute `{self.field_name}` length should be >= {self.min_size}")
        elif self.max_size is not None and len(value) > self.max_size:
            raise ValidationError(f"Attribute `{self.field_name}` length should be <= {self.max_size}")


class Type(BaseValidator):

    def __setup__(self, types):
        self.types = types

    def validate(self, instance, value):
        if not isinstance(value, self.types):
            types_names = ", ".join(type_.__name__ for type_ in self.types)
            raise ValidationError(
                f"Attribute `{self.field_name}` should be an instance of `{types_names}`"
            )


class String(Type):

    def __setup__(self, types=(str,)):
        Type.__setup__(self, types)


class Number(Type):

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
