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
from functools import wraps, lru_cache, reduce

from metautils.box import methodbox


class MetaTemplateBase(object):
    """
    A marker for `MetaTemplate` types.
    """
    pass


class _MetaTemplateMeta(type):
    """
    Constructs `MetaTemplate` objects from type specs.
    This is meta.
    """
    def __new__(mcls,
                name,
                bases,
                dict_,
                preprocess=None,
                decorators=(),
                cachesize=None):
        if not isinstance(bases[0], _MetaTemplateMeta):
            raise TypeError('Template must subclass T')

        bases = bases[1:]
        preprocess = preprocess or (lambda *a: a)
        decorators = tuple(decorators)

        class MetaTemplate(MetaTemplateBase):
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
                dict_cpy = dict_.copy()  # We could potentially mutate this.
                inner_bases = (base,) + bases

                # This function allows us to conditionally modify the class
                # name, bases, or dict after we have recieved the base
                # class. Think of this like a second meta layer.
                name_pp, inner_bases, dict_cpy = preprocess(
                    name, inner_bases, dict_cpy
                )

                inner_base = inner_bases[0]

                for k, v in dict_cpy.items():
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

        return MetaTemplate()


T = type.__new__(_MetaTemplateMeta, 'T', (object,), {
    '___doc__': 'A template paramater',
})


class templated(methodbox):
    """
    Marker to indicate that the method should be passed `T` under the
    name: `T_`
    """
    pass


def compose(*args, _apply_=lambda a, b: b(a)):
    """
    Compose functions.
    """
    def composed(base):
        return reduce(_apply_, reversed(args), base)

    return composed
