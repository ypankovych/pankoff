Usage examples
**************

Basic usage
-----------
Lets create ``data.json`` as following:

.. code-block:: JSON

    {
      "name": "Yaroslav",
      "age": 22,
      "salary": 100,
      "office": "Central Office",
      "position": "Manager",
      "greeting_template": "Hello, {}"
    }

Now lets load it:

.. code-block:: python
    :emphasize-lines: 50

    from pankoff.base import Container
    from pankoff.combinator import combine
    from pankoff.exceptions import ValidationError
    from pankoff.magic import autoinit, Alias
    from pankoff.validators import String, Number, BaseValidator, Predicate, LazyLoad


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


    @autoinit(merge=True)
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
            predicate=lambda instance, value: value == "Manager" and "100 USD" in instance.salary,
            error_message="Invalid value for {field_name}, person got into wrong position: {value}"
        )
        payment = Alias("salary")
        job_desc = LazyLoad(factory=lambda instance: f"{instance.position} at {instance.office}")

        def  __init__(self, greeting_template):
            self.greeting = greeting_template.format(self.name)

    person = Person.from_path("data.json")
    print(person)  # Person(name=Yaroslav, age=22, salary=Yaroslav salary is: 100 USD, office=Central Office, position=Manager, job_desc=Manager at Central Office)
    print(person.greeting)  # Hello, Yaroslav

Trying invalid data
-----------------------------------------------
Change your ``data.json``

.. code-block:: JSON
    :emphasize-lines: 6

    {
      "name": "Yaroslav",
      "age": 22,
      "salary": 100,
      "office": "Central Office",
      "position": "HR",
      "greeting_template": "Hello, {}"
    }

Now load it:

>>> person = Person.from_path("data.json")
Traceback (most recent call last):
...
pankoff.exceptions.ValidationError: ['Invalid value for position, person got into wrong position: HR']

Lets do some transformations
----------------------------

Here's our ``data.json``:

.. code-block:: JSON

    {
        "name": "Yaroslav",
        "salary": "100 USD",
        "kind": 1
    }


.. code-block:: python
    :emphasize-lines: 22

    kinds = {
        1: "Good person",
        2: "Bad person"
    }

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
        kind = KindMutator()

    Person.from_path("data.json").to_path("mutated_data.json", indent=4)

And here's what we get in ``mutated_data.json``:

.. code-block:: JSON

    {
        "name": "Yaroslav",
        "salary": "Yaroslav salary is: 100 USD",
        "kind": "Good person"
    }

.. _Making factories:

Making object factories
-----------------------

It is possible to make object factory based on the same Container class.

.. code-block:: python

    class Multiplication(BaseValidator):

        def validate(self, instance, value):
            if not isinstance(value, (int, float)):
                raise ValidationError(f"`{self.field_name}` should be a number")

        def mutate(self, instance, value):
            return value * instance.get_extra("multiplicator", default=1)

    @autoinit
    class Person(Container):
        name = String()
        age = Multiplication()


    young_person = Person.extra(multiplicator=2)
    old_person = Person.extra(multiplicator=5)

    john = young_person(name="John", age=10)
    yaroslav = old_person(name="yaroslav", age=10)

    print(john)  # Person(name=John, age=20)
    print(yaroslav)  # Person(name=yaroslav, age=50)

As you can see, ``young_person`` and ``old_person`` acting like completely different things, but in fact they're not.

Also, you can access underlying ``extra`` structure by doing ``yaroslav._extra``, which returns ``MappingProxyType`` view.
