# Pankoff

[![Downloads](https://pepy.tech/badge/pankoff)](https://pepy.tech/project/pankoff)
[![Documentation Status](https://readthedocs.org/projects/pankoff/badge/?version=12.0)](https://pankoff.readthedocs.io/?badge=12.0)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/pankoff.svg)](https://pypi.python.org/pypi/pankoff/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/ypankovych/pankoff/graphs/commit-activity)
[![MIT License](https://img.shields.io/pypi/l/pankoff.svg)](https://opensource.org/licenses/MIT)
[![PyPi status](https://img.shields.io/pypi/status/pankoff.svg)](https://pypi.python.org/pypi/pankoff)
[![PyPI version fury.io](https://badge.fury.io/py/pankoff.svg)](https://pypi.python.org/pypi/pankoff/)
[![PyPI implementation](https://img.shields.io/pypi/implementation/pankoff.svg)](https://pypi.python.org/pypi/pankoff/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

Lightweight, flexible, easy to use validation tool. Pure Python, no dependencies.

Validate, mutate, serialize and deserialize with lots of magic.

`pip install --user pankoff`

Read full [documentation here.](https://pankoff.readthedocs.io/)

```
$ cat data.json
{
    "name": "Yaroslav",
    "salary": "100 USD",
    "kind": 1
}
```

```python
from pankoff.base import Container
from pankoff.combinator import combine
from pankoff.exceptions import ValidationError
from pankoff.magic import autoinit
from pankoff.validators import String, BaseValidator, Number

kinds = {
    1: "Good person",
    2: "Bad person"
}


class Salary(BaseValidator):

    def __setup__(self, amount, currency):
        self.amount = amount
        self.currency = currency

    def mutate(self, instance, value):
        return f"{instance.name} salary is: {value}"

    def validate(self, instance, value):
        amount, currency = value.split()
        if int(amount) != self.amount or currency != self.currency:
            raise ValidationError(f"Wrong data in field: `{self.field_name}`")


class KindMutator(BaseValidator):

    def validate(self, instance, value):
        if value not in kinds:
            raise ValidationError(f"Person kind should be in {kinds.keys()}")

    def mutate(self, instance, value):
        return kinds[value]


@autoinit
class Person(Container):
    name = String()
    salary = Salary(amount=100, currency="USD")
    kind = combine(Number, KindMutator)()


if __name__ == "__main__":
    Person.from_path("data.json").to_path("mutated_data.json", indent=4)
```
```
$ cat mutated_data.json
{
    "name": "Yaroslav",
    "salary": "Yaroslav salary is: 100 USD",
    "kind": "Good person"
}
```
