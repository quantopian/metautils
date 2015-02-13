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

from metautils.box import methodbox
from metautils.compat import qualname, reduce, lru_cache, with_metaclass, PY2


# Sentinel value to mark the actual parambase object.
_parambasebase = object()

# Reducer for the iterable of decorators.
_apply = lambda a, b: b(a)


class _MetaFactoryMeta(type):
    """
    Constructs `MetaFactory` objects from type specs.
    This is meta.
    """
    def __new__(mcls, name, bases, dict_):
        if bases and bases[0] is _parambasebase:
            # Construct a concrete object for _parambase classes.
            return type.__new__(mcls, name, (object,), dict_)

        if not bases or not isinstance(bases[0], _MetaFactoryMeta):
            raise TypeError(
                'metaclass templates must use a base class constructed with: '
                '{fn}'.format(fn=qualname(parambase)),
            )

        parambase_ = bases[0]
        bases_rest = bases[1:]  # strip the `parambase` object out.
        transform = parambase_._transform
        preprocess = parambase_._preprocess
        cachesize = parambase_._cachesize

        # If this is a generator, pull them out now and save them.
        decorators = tuple(parambase_._decorators)

        class MetaFactory(object):
            """
            A callable that takes a base metaclass and returns a new metaclass
            that is a composition of this metaclass template and a base
            metaclass.
            """
            __slots__ = ()

            def __call__(self, base=type, adjust_name=True):
                """
                Constructs a new metaclass that is the composition of this
                metaclass template and a base metaclass.

                If `adjust_name` is truthy, the name of the base class will be
                prepended with the name of the new class.
                """
                # Transform the base class and create the actual bases.
                base = transform(base)
                bases = (base,) + bases_rest

                dict_cpy = dict_.copy()  # We could potentially mutate this.

                if preprocess:
                    # This function allows us to conditionally modify the class
                    # name, bases, or dict after we have recieved the base
                    # class. Think of this like a second meta layer.
                    name_pp, bases, dict_pp = preprocess(name, bases, dict_cpy)

                for k, v in dict_.items():
                    if isinstance(v, withbase):
                        # The method needs the base class in a closure, so we
                        # construct one here.
                        def close_by_value(unboxed=v.unboxed):
                            # This is the dumbest python scoping issue.
                            @wraps(unboxed)
                            def wrapper(*args, **kwargs):
                                return unboxed(*args, __base__=base, **kwargs)

                            return wrapper

                        dict_pp[k] = close_by_value()

                if adjust_name:
                    # We want to have the bases name prepended to ours.
                    name_pp = base.__name__ + name_pp

                tp = reduce(
                    _apply,
                    decorators,
                    type(name_pp, bases, dict_cpy),
                )

                if not PY2:
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

        return MetaFactory()


def parambase(transform=None, preprocess=None, decorators=(), cachesize=None):
    """
    Returns a marker class for the paramater in the class definition.
    This takes:
      - A trasform function to be applied to the base class before
        constructing the class.
      - A preprocess function for adjusting the name, bases, and dict_ before
        constructing the class.
      - An iterable of class decorators to be applied in order on the class.

    The actual argument will be passed to all functions marked with:
    `withbase` by keyword as the name `__base__`.
    """
    class _parambase(with_metaclass(_MetaFactoryMeta, _parambasebase)):
        __slots__ = ()
        _transform = staticmethod(transform or (lambda base: base))
        _preprocess = staticmethod(preprocess or (lambda *args: args))
        _decorators = decorators
        _cachesize = cachesize

    return _parambase


class withbase(methodbox):
    """
    Marker to indicate that the given method needs to be passed the base
    class under the name `__base__`
    """
    pass


def compose(*factories):
    """
    Composes arbitrary metaclass factories.
    """
    return lambda base: reduce(_apply, factories, base)
