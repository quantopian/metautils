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
PY2 = True

try:
    reduce
except NameError:
    PY2 = False

PY3 = not PY2

from six import with_metaclass


if PY2:
    def qualname(obj):
        return '.'.join((obj.__module__, obj.__name__))

    from functools32 import lru_cache

else:  # PY3
    def qualname(obj):
        return obj.__qualname__

    from functools import reduce, lru_cache


__all__ = [
    'PY2',
    'PY3',
    'lru_cache',
    'qualname',
    'reduce',
    'with_metaclass'
]
