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
import math
import operator

from sys import version_info


PY2 = version_info.major == 2
PY3 = not PY2

if PY2:
    from functools32 import lru_cache

    reduce = reduce  # noqa

    def qualname(obj):
        """
        Returns the qualified name of `obj`.
        """
        return '.'.join(obj.__module__, obj.__name__)

    def items(dict_):
        return dict_.iteritems()

    def values(dict_):
        return dict_.itervalues()

else:
    from functools import lru_cache, reduce

    def qualname(obj):
        """
        Returns the qualified name of `obj`.
        """
        return obj.__qualname__

    def items(dict_):
        return dict_.items()

    def values(dict_):
        return dict_.values()


def _apply(a, b):
    return b(a)


def _composed_doc(fs):
    """
    Generate a docstring for the composition of fs.
    """
    if not fs:
        # Argument name for the docstring.
        return 'n'

    return '{f}({g})'.format(f=fs[0].__name__, g=_composed_doc(fs[1:]))


def compose(*fs):
    """
    Compose functions together in order:

    compose(f, g, h) = lambda n: f(g(h(n)))
    """
    # Pull the iterator out into a tuple so we can call `composed`
    # more than once.
    rs = tuple(reversed(fs))

    def composed(n):
        return reduce(lambda a, b: b(a), rs, n)

    # Attempt to make the function look pretty with
    # a fresh docstring and name.
    try:
        composed.__doc__ = 'lambda n: ' + _composed_doc(fs)
    except AttributeError:
        # One of our callables does not have a `__name__`, whatever.
        pass
    else:
        # We already know that for all `f` in `fs`, there exists `f.__name__`
        composed.__name__ = '_of_'.join(f.__name__ for f in fs)

    return composed


_nlname = '_NonLocal__nl'


class _MagicExpansionMeta(type):
    """
    A metaclass for expanding the @reflected and @inplace decorators.
    """
    def __new__(mcls, name, bases, dict_):
        for v in values(dict(dict_)):
            aliases = getattr(v, '_aliases', ())
            for alias in aliases:
                dict_[alias] = v

        return super(_MagicExpansionMeta, mcls).__new__(
            mcls, name, bases, dict_,
        )


def _alias(f, prefix):
    name = f.__name__
    if not name.startswith('__') and name.endswith('__'):
        raise ValueError('%s must be a dunder method' % name)

    name = name[2:-2]
    aliases = getattr(f, '_aliases', set())
    aliases.add('__%s%s__' % (prefix, name))
    f._aliases = aliases


def _reflected(f):
    """
    Aliases this magic with the reflected version.
    """
    _alias(f, 'r')
    return f


def _inplace(f):
    """
    Aliases this magic with the inplace version.
    """
    _alias(f, 'i')
    return f


class NonLocal(object):
    """
    NonLocal value for testing, backwards compat for py2.
    """
    def __init__(self, nl):
        object.__setattr__(self, _nlname, nl)

    def __getattribute__(self, attr):
        if attr == _nlname:
            return object.__getattribute__(self, attr)

        return getattr(self.__nl, attr)

    def __setattr__(self, attr, val):
        return setattr(self.__nl, attr, val)

    def __eq__(self, other):
        return self.__nl == other

    def __ne__(self, other):
        return self.__nl != other

    def __lt__(self, other):
        return self.__nl < other

    def __gt__(self, other):
        return self.__nl > other

    def __le__(self, other):
        return self.__nl <= other

    def __ge__(self, other):
        return self.__nl >= other

    def __pos__(self):
        return +self.__nl

    def __neg__(self):
        return -self.__nl

    def __abs__(self):
        return abs(self.__nl)

    def __invert__(self):
        return ~self.__nl

    def __round__(self):
        return round(self.__nl)

    def __floor__(self):
        return math.floor(self.__nl)

    def __ceil__(self):
        return math.ceil(self.__nl)

    def __trunc__(self):
        return math.truc(self.__nl)

    @_reflected
    @_inplace
    def __add__(self, other):
        return self.__nl + other

    @_reflected
    @_inplace
    def __sub__(self, other):
        return self.__nl - other

    @_reflected
    @_inplace
    def __mul__(self, other):
        return self.__nl * other

    @_reflected
    @_inplace
    def __floordiv__(self, other):
        return self.__nl // other

    @_reflected
    @_inplace
    def __div__(self, other):
        return self.__nl / other

    @_reflected
    @_inplace
    def __truediv__(self, other):
        return operator.truediv(self.__nl, other)

    @_reflected
    @_inplace
    def __mod__(self, other):
        return self.__nl % other

    @_reflected
    @_inplace
    def __divmod__(self, other):
        return divmod(self.__nl, other)

    @_reflected
    @_inplace
    def __pow__(self, other):
        return self.__nl ** other

    @_reflected
    @_inplace
    def __lshift__(self, other):
        return self.__nl << other

    @_reflected
    @_inplace
    def __rshift__(self, other):
        return self.__nl >> other

    @_reflected
    @_inplace
    def __and__(self, other):
        return self.__nl & other

    @_reflected
    @_inplace
    def __or__(self, other):
        return self.__nl | other

    @_reflected
    @_inplace
    def __xor__(self, other):
        return self.__nl ^ other

    def __int__(self):
        return int(self.__nl)

    def __float__(self):
        return float(self.__nl)

    def __complex__(self):
        return complex(self.__nl)

    def __oct__(self):
        return oct(self.__nl)

    def __hex__(self):
        return hex(self.__nl)

    def __index__(self):
        return self.__nl.__index__()

    def __str__(self):
        return str(self.__nl)

    def __bytes__(self):
        return bytes(self.__nl)

    def __repr__(self):
        return repr(self.__nl)

    def __format__(self, formatstr):
        return self.__nl.__format__(formatstr)

    def __hash__(self):
        return hash(self.__nl)

    def __bool__(self):
        return bool(self.__nl)

    def __dir__(self):
        return dir(self.__nl)

    def __delattr__(self, name):
        return delattr(self.__nl, name)

    def __len__(self):
        return len(self.__nl)

    def __getitem__(self, key):
        return self.__nl[key]

    def __setitem__(self, key, value):
        self.__nl[key] = value

    def __delitem__(self, key):
        del self.__nl[key]

    def __iter__(self):
        return iter(self.__nl)

    def __reversed__(self):
        return reversed(self.__nl)

    def __contains__(self, item):
        return item in self.__nl

    def __missing__(self, key):
        return self.__nl.__missing__[key]

    def __instancecheck__(self, instance):
        return isinstance(self.__nl, instance)

    def __call__(self, *args, **kwargs):
        return self.__nl(*args, **kwargs)

    def __enter__(self):
        return self.__nl.__enter__()

    def __exit__(self, exc_type, exc_value, exc_tb):
        return self.__nl.__exit__(exc_type, exc_value, exc_tb)

    def __get__(self, instance, owner):
        return self.__nl.__get__(instance, owner)

    def __set__(self, instance, value):
        return self.__nl.__get__(instance, value)

    def __delete__(self, instance):
        return self.__nl.__delete__(instance)

    def __prepare__(self, name, bases):
        return self.__nl.__prepare__(name, bases)

    def __next__(self):
        return next(self.__nl)

    # PY2 support:
    if PY2:
        __nonzero__ = __bool__
        # I can probably leave this; however, this is not the py2 convention.
        del __bool__

        def __coerce__(self, other):
            return self.__nl.__coerce__(other)

    @staticmethod
    def reassign(nl, val):
        object.__setattr__(nl, _nlname, val)


__all__ = [
    'NonLocal',
    'PY2',
    'PY3',
    'compose',
    'items',
    'lru_cache',
    'qualname',
    'reduce',
    'values',
]
