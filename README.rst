metautils
=========

Utilities for writing and composing metaclasses.

Metaclass Template Model
-----------------------

Why do we need or want to write metaclass templates.

Consider the two metaclasses.

.. code:: python

    class AllLower(type):
        def __new__(mcls, name, bases, dict_):
            dict_ = {k.lower(): v for k, v in dict_.items()}
            return super().__new__(mcls, name, bases, dict_)


    class MethodCatcher(type):
        def __new__(mcls, name, bases, dict_):
            dict_['methods'] = [v for v in dict_.values() if callable(v)]
            return super().__new__(mcls, name, bases, dict_)

What would we do if we wanted to make a class that used *BOTH* of these
metaclasses? Using a class that subclasses both ``AllLower`` and
``MethodCatcher`` does not work, what we want is a way to chain them.

With the metaclass template model, we could have written our metaclasses
as:

.. code:: python

    from metautils import T, templated

    class AllLower(T):
        @templated
        def __new__(mcls, name, bases, dict_, T_):
            dict_ = {k.lower(): v for k, v in dict_.items()}
            return T_.__new__(mcls, name, bases, dict_)


    class MethodCatcher(T):
        @templated
        def __new__(mcls, name, bases, dict_, T_):
            dict_['methods'] = [v for v in dict_.values() if callable(v)];
            return T_.__new__(mcls, name, bases, dict_)

Now we can define classes that use *BOTH* of these metaclasses like so:

.. code:: python

    class C(object, metaclass=MethodCatcher(AllLower())):
        def F():
            pass

        def g():
            pass

        a = 'a'
        B = 'b'

We can see that this applied the composition of the metaclasses.

.. code:: python

    >>> C.f
    <function __main__.C.F>
    >>> C.g
    <function __main__.C.g>
    >>> C.b
    'b'
    >>> C.a
    'a'
    >>> C.methods
    [<function __main__.C.g>, <function __main__.C.F>]

The order that the metaclasses are composed is explicit as they act as
transformers over each other.

``parambase``
-------------

This function retuns base classes that will make your metaclass a
metaclass template.

``parambase`` takes the folling arguments:

-  ``transform``: A function to apply to the input base before
   proceding. This function should take a ``type`` and return a new
   ``type``. ``default``: Apply no transform function (``None``).
-  ``preprocess``: A function that takes the ``name, bases, dict_`` and
   returns any modifications that you would like to make BEFORE
   constructing the class object. This allows for conditional
   definitions of the class dict. The ``bases`` passed at this step will
   have the input paramater as ``bases[0]``. ``default``: Apply no
   preprocessing (``None``).
-  ``decorators``: An iterable of class decorators to apply to the newly
   constructed type. ``default``: ``()``.
-  ``cachesize``: For performance, metaclass templates will use a
   ``lru_cache``. This is the size of the cache to hold. If this value
   is ``< 0``, then no cache will be used. ``default``: No maximum size
   (``None``).

When you make a metaclass that subclasses ``T`` the name of the class will be
bound to a ``MetaClassTemplate`` object instead of a ``type`` object.

``MetaClassTemplate``
--------------------

A ``MetaClassTemplate`` is a callable that takes a ``type`` object and
returns a new ``type`` object. It takes the following arguments:

-  ``base``: A type object. ``default``: ``type``.
-  ``adjust_name``: Should we prepend the name of the ``base`` to the
   new type object. ``default``: ``True``.

These can be chained together with any concrete metaclass at the end,
e.g.:

.. code:: python

    new_metaclass = m(n,p(q(...z(type)...)))

You can also use the compose function to do this:

.. code:: python

    from metautils import compose

    new_metaclass_template = compose(m, n, p, q, ..., z)
