.. _Chain:

Chaining validators
*******************
It is possible to combine validators together. There's a few ways to do this, I'll go over them below.

.. autofunction:: pankoff.combinator.combine

Using ``combine()`` function
============================

``combine()`` allows you to do exactly 2 things, create "raw" combined validator, or
create combined "instance".

Lets create "raw" combined validator first:

.. code-block:: python
    :emphasize-lines: 5

    from pankoff.magic import autoinit
    from pankoff.combinator import combine
    from pankoff.validators import String, Sized

    sized_name = combine(String, Sized)

Now, we can actually use it to create instances:

.. code-block:: python
    :emphasize-lines: 3

    @autoinit
    class Person:
        name = sized_name(min_size=5)

    guido = Person(name="Guido")
    print(guido.name)  # Guido

Alternatively, you can create instance straight away:

.. code-block:: python
    :emphasize-lines: 3

    @autoinit
    class Person:
        name = combine(String, Sized, min_size=5)

    guido = Person(name="Guido")
    print(guido.name)  # Guido


Using "and" operator
====================
Besides ``combine()`` function, you can chain validators using ``&`` operator,
it'll create a "raw" validator for you:

>>> raw_validator = Sized & String & Number & Type
>>> raw_validator
Combination of (Sized, String, Number, Type) validators
>>> validator = raw_validator(...)
>>> validator
CombinedValidator(Sized, String, Number, Type)

Using inheritance
=================
Chaining uses inheritance mechanism under the hood, so you can do the following:

.. code-block:: python
    :emphasize-lines: 1

    class MyCombinedValidator(String, Sized, ...):
        pass
