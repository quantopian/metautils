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
from unittest import TestCase

from metautils import T, templated
from metautils.template import TemplateBase
from metautils.box import box


class TestMeta(type):
    """
    A metaclass for testing.
    """
    pass


class MetaFactoryTestCase(TestCase):
    def test_create_template(self):
        """
        Tests that subclassing T returns a template.
        """
        class template(T):
            pass

        self.assertIsInstance(template, TemplateBase)

    def test_applies_decorators(self):
        test_decorator_called = 0

        def test_decorator(cls):
            nonlocal test_decorator_called
            test_decorator_called += 1

            self.assertIsInstance(cls, a)
            cls = cls.unboxed

            self.assertIsInstance(cls, b)
            cls = cls.unboxed

            self.assertIsInstance(cls, c)
            cls = cls.unboxed

            self.assertIsInstance(cls, type)
            return cls

        class a(box):
            pass

        class b(box):
            pass

        class c(box):
            pass

        class template(T, decorators=(test_decorator, a, b, c,)):
            pass

        class C(object, metaclass=template()):
            pass

        self.assertEqual(test_decorator_called, 1)

    def test_correct_base_no_tsfm(self):
        """
        Tests that `__base__` is the correct object without a transform
        function.
        """
        class M(T):
            @templated
            def __new__(mcls, name, bases, dict_, T_):
                return T_

        class C(object, metaclass=M()):
            """
            A class that uses the default, test that this is `type`.
            """
            pass
        self.assertIs(C, type)

        class D(object, metaclass=M(TestMeta)):
            """
            A use where the meta explictly subclasses.
            """
            pass
        self.assertIs(D, TestMeta)

    def test_correct_base_tsfm(self):
        """
        Tests that preprocess can change the base.
        """
        class tsfmmarker(object):
            pass

        def preprocess(name, bases, dict_):
            class tsfm(bases[0], tsfmmarker):
                pass

            return name, (tsfm,) + bases[1:], dict_

        class M(T, preprocess=preprocess):
            @templated
            def __new__(mcls, name, bases, dict_, T_):
                return T_

        class C(object, metaclass=M()):
            """
            A class that uses the default, test that this is `type`.
            """
            pass
        self.assertIs(C.__base__, type)
        self.assertIs(C.__bases__[1], tsfmmarker)

        class D(object, metaclass=M(TestMeta)):
            """
            A use where the meta explictly subclasses.
            """
            pass
        self.assertIs(D.__base__, TestMeta)
        self.assertIs(D.__bases__[1], tsfmmarker)
