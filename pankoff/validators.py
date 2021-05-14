import numbers

from pankoff.base import BaseValidator
from pankoff.exceptions import ValidationError


class Sized(BaseValidator):

    def __setup__(self, min_size=None, max_size=None):
        self.min_size = min_size
        self.max_size = max_size

    def validate(self, instance, value):
        if self.min_size is not None and len(value) < self.min_size:
            raise ValidationError(f"Attribute `{self.attr_name}` length should be >= {self.min_size}")
        elif self.max_size is not None and len(value) > self.max_size:
            raise ValidationError(f"Attribute `{self.attr_name}` length should be <= {self.max_size}")


class Type(BaseValidator):

    def __setup__(self, types):
        self.types = types

    def validate(self, instance, value):
        if not isinstance(value, self.types):
            raise ValidationError(f"Attribute `{self.attr_name}` should be an instance of `{self.types}`")


class String(Type):

    def __setup__(self, types=(str,)):
        super(String, self).__setup__(types)


class Number(Type):

    def __setup__(self, min_value=None, max_value=None, types=(numbers.Number,)):
        super(Number, self).__setup__(types)
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, instance, value):
        super(Number, self).validate(instance, value)
        if self.min_value is not None and value < self.min_value:
            raise ValidationError(f"Attribute `{self.attr_name}` should be >= {self.min_value}")
        elif self.max_value is not None and value > self.max_value:
            raise ValidationError(f"Attribute `{self.attr_name}` should be <= {self.max_value}")
