# Here's full usage example:
```python
from pankoff.combinator import combine
from pankoff.validators import Sized, String, Number, Type, BaseValidator


class Salary(BaseValidator):

    def __setup__(self, amount, currency):
        self.amount = amount
        self.currency = currency

    def validate(self, instance, value):
        amount, currency = value.split()
        if int(amount) != self.amount or currency != self.currency:
            raise ValueError(f"Wrong salary in field: `{self.attr_name}`")


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


person = Person(
    name="John",
    age=18,
    backpack=[1, 2, 3, 4, 5],
    salary="100 USD"
)
```
## Now, lets try invalid data:
```python

person = Person(
    name="John",
    age=18,
    backpack=(1, 2, 3, 4),
    salary="100 USD"
)
# pankoff.exceptions.ValidationError: ["Attribute `backpack` should be an instance of `(<class 'list'>,)`", 'Attribute `backpack` length should be >= 5']
```
## combine() function
You can use `comdine(...)` to combine many validators.

If has 2 possible invocation ways:
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
```