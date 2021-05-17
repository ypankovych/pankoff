from pankoff.base import BaseValidator

init_template = "def __init__({arguments}):\n\t{assignments}"


def autoinit(klass=None, verbose=False):
    def inner(cls):
        if cls.__init__ is not object.__init__:
            raise RuntimeError(f"{cls} already has __init__ method defined")

        attrs = ["self"]
        assignments = []
        namespace = {}
        for attr in vars(cls).values():
            if isinstance(attr, BaseValidator):
                attrs.append(attr.field_name)
                assignments.append(f"self.{attr.field_name} = {attr.field_name}")
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
