#
# Copyright 2015 Quantopian, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from functools import wraps
from textwrap import dedent

from metautils.box import methodbox
from metautils.compat import compose, items, lru_cache


class TemplateBase(object):
    """
    A marker for `Template` types.
    """


class _TemplateMeta(type):
    """
    Constructs `ClassTemplate` objects from type specs.
    This is meta.
    """
    def __new__(mcls,
                name,
                bases,
                dict_,
                preprocess=None,
                decorators=(),
                cachesize=None):

        template_param = bases[0]
        if not isinstance(template_param, _TemplateMeta):
            raise TypeError('class template must subclass T')

        bases = bases[1:]

        if issubclass(template_param, _TWithArgs):
            # The arguments were passed through the template param,
            # forward these to `__new__` to emulate python 3 class arguments.
            return mcls.__new__(
                mcls,
                name,
                (T,) + bases,  # Kill the infinite recursion.
                dict_,
                **template_param._kwargs
            )

        preprocess = preprocess or (lambda *a: a)
        decorators = tuple(decorators)

        class Template(TemplateBase):
            """
            A callable that takes a base class and returns a new class
            that is a composition of this class template and a base class.

            Parameters
            ----------
            base : type
                The class to create a subclass of.

            Returns
            -------
            subclass : type
                A subclass of ``base`` with the body of this template.
            """
            # Copy the docstring from the template if provided.
            __doc__ = dict_.get('__doc__', __doc__)
            __slots__ = ()

            def __call__(self, base=type, adjust_name=True):
                """
                Constructs a new class that is the composition of this
                class template and a base class.

                Parameters
                ----------
                base : type, optional
                    The class to create a subclass of.
                adjust_name : bool, optional
                    Should the name of the resulting subclass be adjusted
                    to include the name of the base class.

                Returns
                -------
                subclass : type
                    A subclass of ``base`` with the body of this template.
                """
                dict_cpy = dict_.copy()  # We could potentially mutate this.
                inner_bases = (base,) + bases

                # This function allows us to conditionally modify the class
                # name, bases, or dict after we have recieved the base
                # class. Think of this like a second meta layer.
                name_pp, inner_bases, dict_cpy = preprocess(
                    name, inner_bases, dict_cpy
                )

                inner_base = inner_bases[0]

                for k, v in items(dict_cpy):
                    if isinstance(v, templated):
                        # The method needs the base class in a closure, so we
                        # construct one here.
                        def close_by_value(unboxed=v.unboxed):
                            # This is the dumbest python scoping issue.
                            @wraps(unboxed)
                            def wrapper(*args, **kwargs):
                                return unboxed(*args, T_=inner_base, **kwargs)

                            return wrapper

                        dict_cpy[k] = close_by_value()

                if adjust_name:
                    # We want to have the base's name prepended to ours.
                    name_pp = base.__name__ + name_pp

                tp = compose(*decorators)(type(name_pp, inner_bases, dict_cpy))
                # This is Python 3 specific, but there is no need to make
                # a check as this will not fail in Python 2, it is just
                # not used.
                tp.__qualname__ = name_pp
                return tp

            if cachesize is None or cachesize >= 0:
                __call__ = lru_cache(cachesize)(__call__)

            def __repr__(self):
                return '<{cls}: {name} at 0x{id_}>'.format(
                    cls=type(self).__name__,
                    name=name,
                    id_=hex(id(self)),
                )

            __str__ = __repr__

        return Template()


class _TWithArgs(object):
    """
    Marker to indicate that this is a template argument that is holding the
    arguments.
    """


def T_new(cls, **kwargs):
    """
    `__new__` for `T`. This allows us to pass argument to the metaclass
    in Python 2.
    """
    # We are using `type.__new__` so that we get a concrete class, not
    # a template.
    return type.__new__(_TemplateMeta, 'TWithArgs', (_TWithArgs,), {
        '__doc__': 'A template parameter with arguments applied.',
        '__slots__': (),
        '_kwargs': kwargs,
    })


# The template parameter. This uses `type.__new__` because we need a concrete
# class here, not a template.
T = type.__new__(_TemplateMeta, 'T', (object,), {
    '__doc__': dedent(
        """
        A template parameter similar to c++ class templates.

        Class templates are defined by 'subclassing' `T`.
        For example:

        >>> class MyTemplate(T):
        ...    @templated
        ...    def method(self, T_):
        ...        print(T_, 'is the template argument')

        To construct instances of your templated class, call the
        template with the class you want to subclass.

        >>> NewClass = MyTemplate(MyBaseClass)
        >>> NewClass.__base__ == MyBaseClass
        True
        >>> NewClass.__mro__ = (MyBaseClass,) + MyBaseClass.__mro__
        True

        The `templated` decorator will pass the templated argument to the
        function implicitly allowing us to close over the base class.

        >>> NewClass().method()
        'MyBaseClass is the template argument'

        Additional arguments can be passed to the template as keyword
        arguments in the class statement, or as arguments to `T`.

        >>> class Python3Style(T, decorators=(mydecorator,)):
        ...     pass

        or in Python 2 without class arguments:

        >>> class Python2Style(T(decorators=(mydecorator,))):
        ...     pass

        Python 2 style will work in Python 2 or 3, so it should be used
        for cross compatible code; however, the Python 3 style looks
        much better and should be used if no python 2 compatibility is
        needed. In Python 3, passing arguments through the template
        argument will override the arguments passed to the class by keyword.

        The arguments may include:

        preprocess: A function that takes the name, bases, and dict_
          of the class before it is generated and returns a new name,
          bases, and dict_. This allows you to change any of these
          class parameters before the class is constructed but after
          the template argument has been passed. The template argument
          will be `bases[0]`.

        decorators: An iterable of class decorators to apply to the
          newly constructed class object.

        cachesize: Because templates are normally used to construct
          classes dynamically, we frequently will pass the same base
          classes in multiple places. To make this more efficient,
          we can `lru_cache` the class factory. This is the argument
          that will be the `lru_cache`'s cachesize. If this is less
          than 0, no cache will be used. If this is `None`, then there
          will be no upper bounds on the cache.
        """,
    ),
    '__new__': T_new,
    '__slots__': (),
})


class templated(methodbox):
    """
    Marker to indicate that the method should be passed `T` under the
    name: `T_`
    """
