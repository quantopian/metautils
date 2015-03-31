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


class box(object):
    """
    A wrapper for an object.

    These can be used as marker types for metaclasses to check for wrapped
    attributes.
    """
    __slots__ = ('_a',)

    def __init__(self, a):
        self._a = a

    @property
    def unboxed(self):
        return self._a


class methodbox(box):
    """
    A box that holds methods.
    """
    __slots__ = box.__slots__

    def __init__(self, a):
        if not callable(a):
            raise TypeError(
                '{cls} must wrap a callable'.format(
                    cls=type(self).__name__,
                ),
            )

        super(methodbox, self).__init__(a)
