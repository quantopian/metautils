from abc import abstractmethod
from metautils.abc import ABCMetaTemplate


def make_class(self):
    class C(object):
        __metaclass__ = ABCMetaTemplate(self.M)

        @abstractmethod
        def abstract_method(self):
            pass

    return C
