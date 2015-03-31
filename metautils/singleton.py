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
from metautils import T, templated


def _singleton_new(cls, *args, **kwargs):
    """
    An invalid new for singleton objects.
    """
    raise TypeError(
        "'{0}' cannot be instantiated because it is a singleton".format(
            cls.__name__,
        ),
    )


class Singleton(T):
    """
    Turns a class statement into an object instantiation to create a
    single instance of a class.

    This is like the `object` keyword from scala; however, this
    does not support companion objects.
    """
    @templated
    def __new__(mcls, name, bases, dict_, T_, **kwargs):
        dict_['__name__'] = name
        cls = T_.__new__(mcls, name, bases, dict_)
        inst = cls(**kwargs)
        # Prevent another instance from being made.
        cls.__new__ = _singleton_new
        return inst
