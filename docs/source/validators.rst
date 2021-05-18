Using validators
****************
Pankoff defines a small preset of validator, and it allow you to define your own.

Default validators
==================
By default, Pankoff defines a few validators, ``String``, ``Number``, ``Type``, ``Sized``,
``Predicate``. We'll go over each one below.

.. autoclass:: pankoff.validators.String()

    >>> @autoinit
    >>> class Person:
    ...     name  = String()

    >>> person = Person(name="Guido")

.. autoclass:: pankoff.validators.Number(mix_value=None, max_value=None)

    >>> @autoinit
    >>> class Person:
    ...     age = Number(min_value=18, max_value=100)

    >>> person = Person(age=25)


.. autoclass:: pankoff.validators.Type(types=(int, str, ...))

    >>> @autoinit
    >>> class Car:
    ...     speed = Type(types=(int, float))

    >>> car = Car(speed=500.4)

.. autoclass:: pankoff.validators.Sized(min_size=None, max_size=None)

    >>> @autoinit
    >>> class Box:
    ...     size = Sized(min_size=20, max_size=50)

    >>> box = Box(size=40)

.. autoclass:: pankoff.validators.Predicate(predicate, default=None, error_message=None)

    >>> @autoinit
    >>> class Person:
    ...     salary = Predicate(
    ...         predicate=lambda instance, value: value == "100 USD",
    ...         default=lambda instance, value: str(value) + " USD"
    ...     )

    >>> person = Person(salary=100)
    >>> person.salary
    "100 USD"

    As you can see, we just turned ``100`` into ``"100 USD"``. You can also chain (see :doc:`combinator`) ``Predicate`` with other validators, and
    normalized value will be propagated to further validators.

    ``Predicate`` supports rich error messages:

    >>> @autoinit
    >>> class Car:
    ...     speed = Predicate(
    ...         predicate=lambda instance, value: value == 100,
    ...         error_message="Invalid value in field: {field_name}, got {value} for {predicate}"
    ...     )

    >>> car = Car(speed=50)
    Traceback (most recent call last):
    ...
    pankoff.exceptions.ValidationError: ['Invalid value in field: speed, got 50 for <lambda>']

Custom validators
=================

You can define you ows validator by subclassing ``BaseValidator``.

>>> from pankoff.base import BaseValidator
>>> from pankoff.exceptions import ValidationError

>>> class EnumValidator(BaseValidator):
...     def __setup__(self, allowed_values):
...         self.allowed_values = allowed_values
...     def validate(self, instance, value):
...         if value not in self.allowed_values:
...             raise ValidationError(
...                 f"Invalid value in field {self.field_name}, value should be in {self.allowed_values} "
...                 f"got {value}"
...             )

It is required for validators to define ``validate``, but ``__setup__`` is optional.