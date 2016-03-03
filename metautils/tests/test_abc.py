from unittest import TestCase

from metautils.compat import PY3


class ABCMetaTemplateTestCase(TestCase):
    class M(type):
        def __new__(mcls, name, bases, dict_):
            dict_['M'] = True
            return super(ABCMetaTemplateTestCase.M, mcls).__new__(
                mcls,
                name,
                bases,
                dict_,
            )

    if PY3:
        from ._test_abc_py3 import make_class
    else:
        from ._test_abc_py2 import make_class  # noqa

    def test_abc(self):
        with self.assertRaises(TypeError) as e:
            self.make_class()()

        self.assertIn('abstract_method', str(e.exception))
