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

from metautils import T
from metautils.template import TemplateBase
from metautils.compat import PY2


class MetaFactoryTestCase(TestCase):
    def test_create_template(self):
        """
        Tests that subclassing T returns a template.
        """
        class template(T):
            """template doc"""
            pass

        self.assertIsInstance(template, TemplateBase)
        self.assertEqual(template.__doc__, 'template doc')


if PY2:
    from metautils.tests._test_template_py2 import Py2TestCase  # NOQA
else:
    from metautils.tests._test_template_py3 import Py3TestCase  # NOQA
