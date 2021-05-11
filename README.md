# python-class-pipelines

```python
from pipelined import Pipelined


class Foo(Pipelined):
    def __init__(self, initial):
        self.initial = initial

    def say(self):
        return self.initial + " fucking"

    def say(self, text):
        return text + " world"

    def say(self, text):
        return text + "!"

    def say(self, text):
        return text.title()


obj = Foo("hello")
print(obj.say())  #  Hello Fucking World!
```