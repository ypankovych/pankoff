Validating data
***************

You can validate data using different methods for different use cases. Obvious case is to just create an instance of
your class with validators defined in it, which we covered in previous sections.

But there's a few more options to it.

You can inherit some capabilities by subclassing ``pankoff.base.Container``.

.. autoclass:: pankoff.base.Container
    :members:

Lets validate JSON directly:

>>> from pankoff.base import Container

>>> @autoinit
>>> class Person(Container):
...     name = String()
...     age = Number(min_value=18)

>>> data = """{"name": "John", "age": 18}"""
>>> obj = Person.from_json(data)
>>> obj.name
"John"
>>> obj.age
18

Besides that, there's 2 more method, ``validate`` and ``is_valid``.

>>> Person.validate({"name": "Carl", "age": 17})
Traceback (most recent call last):
...
pankoff.exceptions.ValidationError: ['Attribute `age` should be >= 18']

>>> Person.is_valid({"name": "Carl", "age": 17})
False

There's also ``from_dict`` method, e,g ``Person.from_dict({...})``.

Validation errors
=================

.. autoclass:: pankoff.exceptions.ValidationError
