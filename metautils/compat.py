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
try:
    reduce = reduce
    PY2 = True
except NameError:
    PY2 = False

PY3 = not PY2

if PY2:
    from functools32 import lru_cache

    def qualname(obj):
        """
        Returns the qualified name of `obj`.
        """
        return '.'.join(obj.__module__, obj.__name__)

    def items(dict_):
        return dict_.iteritems()

else:
    from functools import lru_cache, reduce

    def qualname(obj):
        """
        Returns the qualified name of `obj`.
        """
        return obj.__qualname__

    def items(dict_):
        return dict_.items()


__all__ = [
    'PY2',
    'PY3',
    'items',
    'lru_cache',
    'qualname',
    'reduce',
]
