Usage example
*************
Lets create ``data.json`` as following:

.. code-block:: JSON

    {
      "name": "Yaroslav",
      "age": 22,
      "salary": 100,
      "office": "Central Office",
      "position": "Manager"
    }

Now lets load it:

.. code-block:: python
    :emphasize-lines: 44

    from pankoff.base import Container
    from pankoff.combinator import combine
    from pankoff.exceptions import ValidationError
    from pankoff.magic import autoinit, Alias
    from pankoff.validators import String, Number, BaseValidator, Predicate, LazyLoad


    class Salary(BaseValidator):

        def __setup__(self, amount, currency):
            self.amount = amount
            self.currency = currency

        def validate(self, instance, value):
            amount, currency = value.split()
            if int(amount) != self.amount or currency != self.currency:
                raise ValidationError(f"Wrong data in field: `{self.field_name}`")


    @autoinit
    class Person(Container):
        name = String()
        age = Number(min_value=18)
        salary = combine(
            Predicate, Salary,
            # Predicate
            predicate=lambda instance, value: value == "100 USD",
            default=lambda instance, value: str(value) + " USD",
            # Salary
            amount=100, currency="USD"
        )
        office = Predicate(
            predicate=lambda instance, value: value in ["Central Office"],
            error_message="Invalid value for field {field_name}, got {value}"
        )
        position = Predicate(
            # NOTE: we can use `salary` field at this point
            predicate=lambda instance, value: value == "Manager" and instance.salary == "100 USD",
            error_message="Invalid value for {field_name}, person got into wrong position: {value}"
        )
        payment = Alias("salary")
        job_desc = LazyLoad(factory=lambda instance: f"{instance.position} at {instance.office}")

    person = Person.from_path("data.json")
    print(person)  # Person(name=Yaroslav, age=22, salary=100 USD, office=Central Office, position=Manager, job_desc=Manager at Central Office)

Trying invalid data. Change your ``data.json``:

.. code-block:: JSON
    :emphasize-lines: 6

    {
      "name": "Yaroslav",
      "age": 22,
      "salary": 100,
      "office": "Central Office",
      "position": "HR"
    }

Now load it:

>>> person = Person.from_path("data.json")
Traceback (most recent call last):
...
pankoff.exceptions.ValidationError: ['Invalid value for position, person got into wrong position: HR']
