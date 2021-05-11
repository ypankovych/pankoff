from types import MethodType


class Pipeline:
    def __init__(self, funcs):
        if not isinstance(funcs, list):
            funcs = [funcs]
        self.funcs = funcs

    def add(self, func):
        self.funcs.append(func)

    def __call__(self, instance, *args):
        args = [instance] + list(args)
        for func in self.funcs:
            args = [instance] + [func(*args)]
        return args[-1]

    def __get__(self, instance=None, owner=None):
        if not instance and owner:
            return self
        return MethodType(self, instance)


class PipelineNamespace(dict):
    def __setitem__(self, key, value):
        if key in self:
            if not isinstance(self[key], Pipeline):
                super(PipelineNamespace, self).__setitem__(key, Pipeline(self[key]))
            self[key].add(value)
        else:
            super(PipelineNamespace, self).__setitem__(key, value)


class PipelinedMeta(type):
    @classmethod
    def __prepare__(mcs, name, bases):
        return PipelineNamespace()


class Pipelined(metaclass=PipelinedMeta):
    pass
