Limitations
***********

As you may already know, Pankoff uses MRO a lot, because of that, you're not allowed to use
``super().validate()`` and ``super().__setup__()``, instead, you should still subclass validators, but
call directly to ``__setup__`` and `validate`, e.g: ``Type.validate(...)``.