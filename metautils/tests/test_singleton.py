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
from metautils.compat import PY3

py3_body = r"""\

from unittest import TestCase

from metautils.singleton import Singleton
from metautils.compat import NonLocal


class SingletonTestCase(TestCase):
    def test_creates_instance(self):
        class instance(object, metaclass=Singleton()):
            pass

        self.assertNotIsInstance(instance, type)

    def test_has_methods(self):
        class instance(object, metaclass=Singleton()):
            def method(self):
                return 'm'

        self.assertEqual(instance.method(), 'm')

    def test_has_valus(self):
        class instance(object, metaclass=Singleton()):
            a = 'a'

        self.assertEqual(instance.a, 'a')

    def test_single_instance_of_type(self):
        class instance(object, metaclass=Singleton()):
            pass

        with self.assertRaises(TypeError):
            type(instance)()

    def test_new_erasure(self):
        called = NonLocal(0)

        def new(cls):
            NonLocal.reassign(called, called + 1)
            return object.__new__(cls)

        class instance(object, metaclass=Singleton()):
            __new__ = new

        self.assertEqual(called, 1)
        self.assertIsNot(instance.__new__, new)
"""

if PY3:
    exec(py3_body)
