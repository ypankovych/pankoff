from pankoff.base import BaseValidator
from pankoff.validators import UNSET, LazyLoad

init_template = "def __init__({arguments}):\n\t{assignments}"


def autoinit(klass=None, verbose=False):
    """
    Auto generates ``__init__`` method for your class based on its validators.

    :param klass: Class to decorate
    :type klass: type

    :param verbose: In case its ``True``, it'll print out the generated source for ``__init__`` method,
     defaults to ``False``
    :type verbose: bool

    :returns: Same class but with newly created ``__init__``
    :raises RuntimeError: raised in case class already has ``__init__`` defined

    .. code-block:: python
       :emphasize-lines: 1,3

        @autoinit(verbose=True)
        class Person:
            name = String()

    Prints:

    .. code-block::

        Generated __init__ method for <class '__main__.Person'>
        def __init__(self, name):
            self.name = name
    """

    def inner(cls):
        if cls.__init__ is not object.__init__:
            raise RuntimeError(f"{cls} already has __init__ method defined")

        attrs = ["self"]
        assignments = []
        namespace = {"UNSET": UNSET}
        for attr in vars(cls).values():
            if isinstance(attr, BaseValidator):
                if isinstance(attr, LazyLoad):
                    attrs.append(f"{attr.field_name}=UNSET")
                else:
                    attrs.append(attr.field_name)
                assignments.append(f"self.{attr.field_name} = {attr.field_name}")
        attrs.sort(key=lambda item: "=" in item)  # move default parameters to the end
        init = init_template.format(
            arguments=", ".join(attrs),
            assignments="\n\t".join(assignments or ["pass"])
        )
        if verbose:
            print(f"Generated __init__ method for {cls}\n{init}")
        exec(init, namespace)
        cls.__init__ = namespace["__init__"]
        return cls

    if klass is not None:
        return inner(klass)
    return inner


class Alias:
    """
    Create and alias for your fields.

    :param source: Attribute name to reffer to
    :type source: str

    >>> class Person:
    ...     full_person_name = String()
    ...     name = Alias("full_person_name")

    >>> obj = Person("Yaroslav Pankovych")
    >>> obj.name
    "Yaroslav Pankovych"
    """

    def __init__(self, source):
        self.source = source

    def __get__(self, instance, owner):
        if not instance:
            return self
        return getattr(instance, self.source)
