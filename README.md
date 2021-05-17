# Pankoff

Light weight, flexible, easy to use validation tool. Pure Python, no dependencies.

- [Installation](#installation)
- [Full usage example](#heres-full-usage-example)
    - [Creating an instance](#now-lets-create-an-instance)
    - [Validation errors](#lets-try-invalid-data)
- [Predicates](#predicates)
- [Accessing the errors](#accessing-the-errors)
- [Combining validators](#combining-validators)
- [Important limitations](#important-limitations)

## Installation:
`pip install --user pankoff`

## Here's full usage example:
```python
from pankoff.base import Container
from pankoff.combinator import combine
from pankoff.exceptions import ValidationError
from pankoff.validators import Sized, String, Number, Type, BaseValidator, Predicate


class Salary(BaseValidator):

    def __setup__(self, amount, currency):
        self.amount = amount
        self.currency = currency

    def validate(self, instance, value):
        amount, currency = value.split()
        if int(amount) != self.amount or currency != self.currency:
            raise ValidationError(f"Wrong data in field: `{self.field_name}`")


class Person(Container):
    name = String()
    age = Number(min_value=18, max_value=100)
    backpack = combine(Type, Sized, types=(list,), min_size=5)
    payment = combine(
        Predicate, Salary,
        # Predicate
        predicate=lambda instance, value: value == "100 USD",
        default=lambda instance, value: str(value) + " USD",
        # Salary
        amount=100, currency="USD"
    )

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
class Person(Container):
    name = String()
    age = Number(min_value=18, max_value=100)
    backpack = combine(Type, Sized, types=(list,), min_size=5)
    payment = combine(
        Predicate, Salary,
        # Predicate
        predicate=lambda instance, value: value == "100 USD",
        default=lambda instance, value: str(value) + " USD",
        # Salary
        amount=100, currency="USD"
    )

# pass `verbose=True` to `autocommit` in order to see generated source:
@autoinit(verbose=True)
class Person(Container):
    ...
# prints:
"""
def __init__(self, name, age, backpack, payment):
	self.name = name
	self.age = age
	self.backpack = backpack
	self.payment = payment
"""
```
### Now, let's create an instance. There's few possible ways to do it:

Using class constructor directly:
```python
person = Person(
    name="John",
    age=18,
    backpack=[1, 2, 3, 4, 5],
    payment=100
)
```
Create an instance from `dict`:
```python
data = {
  "name": "John",
  "age": 18,
  "backpack": [1, 2, 3, 4, 5],
  "payment": 100
}
person = Person.from_dict(data)
# or simply:
person = Person(**data)
```
And the last one, create an instance from json:
```python
data = """
{
  "name": "John",
  "age": 18,
  "backpack": [1, 2, 3, 4, 5],
  "payment": 100
}
"""
person = Person.from_json(data, loader=json.loads)  # json.loads is default loader
```
### Lets try invalid data:
```python
person = Person(
    name="John",
    age=18,
    backpack=(1, 2, 3, 4),
    payment=100
)
# pankoff.exceptions.ValidationError: ['Attribute `backpack` should be an instance of `list`', 'Attribute `backpack` length should be >= 5']
```
There's a few ways to validate an instance. Use either `Person.validate(data)` which raises in case the data is invalid,
or you can use `Person.is_valid(data)` which returns `True/False`.
```python
Person.validate({
  "name": "John",
  "age": 18,
  "backpack": [1, 2, 3, 4, 5],
  "payment": 10
})  # pankoff.exceptions.ValidationError: ['Wrong data in field: `payment`']
```
```python
print(Person.is_valid({
  "name": "John",
  "age": 18,
  "backpack": [1, 2, 3, 4, 5],
  "payment": 10
})))  # False
```
NOTE: you're not forced to inherit from `Container`, it simply gives you a few additional methods: `is_valid`, 
`from_json`, `from_dict`, `validate`.
## Predicates
As you can see, it is possible to define predicates for your fields, e.g:
```python
@autoinit
class Car:
    windows = combine(
        Predicate, Number,
        # Predicate
        predicate=lambda instance, value: value == 4,
        default=lambda instance, value: int(value) * 2,
        # Number
        min_value=4
    )
```
Now we can actually tweak `windows` count if it doesn't satisfy our predicate, e.g:
```python
car = Car(windows="2")
```
This car considered valid. We just normalized our data using `default` argument of predicate (turned `"2"` into `4`). 

Also, it is possible to specify custom error templates for predicates:
```python
@autoinit
class Car:
    windows = Predicate(
        predicate=lambda instance, value: value == 4,
        error_message="Invalid value for field `{field_name}`, got value {value}. Predicate {predicate} failed."
    )

car = Car(windows="2")
# pankoff.exceptions.ValidationError: ['Invalid value for field `windows`, got value 2. Predicate <lambda> failed.']
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
## Important limitations
As you may already know, Pankoff uses MRO a lot, because of that, you're not allowed to use
`super().validate()` and `super().__setup__()`, instead, you should still subclass validators, but
call directly to `__setup__` and `validate`, e.g: `Type.validate(...)`.