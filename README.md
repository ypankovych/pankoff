# Pankoff (do not use in prod)

Light weight, flexible, easy to use validation tool.

> Q: Why shouldn't i use it in prod?

> A: It manipulates with MRO a lot, so it could be unstable under certain circumstances

- [Installation](#installation)
- [Full usage example](#heres-full-usage-example)
    - [Creating an instance](#now-lets-create-an-instance)
    - [Validation errors](#lets-try-invalid-data)
- [Accessing the errors](#accessing-the-errors)
- [Combining validators](#combining-validators)

## Installation:
`pip install --user pankoff`

## Here's full usage example:
```python
from pankoff.combinator import combine
from pankoff.exceptions import ValidationError
from pankoff.validators import Sized, String, Number, Type, BaseValidator


class Salary(BaseValidator):

    def __setup__(self, amount, currency):
        self.amount = amount
        self.currency = currency

    def validate(self, instance, value):
        amount, currency = value.split()
        if int(amount) != self.amount or currency != self.currency:
            raise ValidationError(f"Wrong data in field: `{self.field_name}`")


class Person:
    name = String()
    age = Number(min_value=18, max_value=100)
    backpack = combine(Type, Sized, types=(list,), min_size=5)
    salary = Salary(amount=100, currency="USD")

    def __init__(self, name, age, backpack, salary):
        self.name = name
        self.age = age
        self.backpack = backpack
        self.salary = salary
```
Also, it is  possible to autogenerate `__init__`:
```python
from pankoff.magic import autoinit

@autoinit
class Person:
    name = String()
    age = Number(min_value=18, max_value=100)
    backpack = combine(Type, Sized, types=(list,), min_size=5)
    salary = Salary(amount=100, currency="USD")

# pass `verbose=True` to `autocommit` in order to see generated source:
@autoinit(verbose=True)
class Person:
    ...
# prints:
"""
def __init__(self, name, age, backpack, salary):
	self.name = name
	self.age = age
	self.backpack = backpack
	self.salary = salary
"""
```
### Now, let's create an instance:
```python
person = Person(
    name="John",
    age=18,
    backpack=[1, 2, 3, 4, 5],
    salary="100 USD"
)
```
### Lets try invalid data:
```python

person = Person(
    name="John",
    age=18,
    backpack=(1, 2, 3, 4),
    salary="100 USD"
)
# pankoff.exceptions.ValidationError: ['Attribute `backpack` should be an instance of `list`', 'Attribute `backpack` length should be >= 5']
```
## Accessing the errors:
```python
try:
    Person(...)
except ValidationError as exc:
    print(exc.errors)
```
## Combining validators 
You can use `combine(...)` to combine many validators.

It has 2 possible invocation ways:
```python
name_validator = combine(String, Sized)
class Foo:
    name = name_validator(min_size=15)
```
Or:
```python
class Foo:
    name = combine(String, Sized, min_size=15)
```
Besides the `combine()`, you can chain validators, e.g:
```python
name_validator = String & Sized & ...
```
Essentially, it is the same as:
```python
class MyCombinedValidator(String, Sized, ...):
    pass
```
All validators could be accessed through `_validators` attribute:
```python
>>> combined_validator = combine(Sized, String, Salary, min_size=5, amount=100, currency="USD")
>>> print(combined_validator._validators)
>>> (<class 'pankoff.validators.Sized'>, <class 'pankoff.validators.String'>, <class '__main__.Salary'>)
```
Also, it has a nice repr:
```python
>>> print(combined_validator)
>>> CombinedValidator(Sized, String, Salary)

>>> print(Sized & String & Number & Type)
>>> Combination of (Sized, String, Number, Type) validators
```
