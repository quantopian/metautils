from __future__ import absolute_import

from abc import ABCMeta

from metautils import T


class ABCMetaTemplate(T, ABCMeta):
    """
    A helper for creating ABC versions of other metaclasses. This creates a
    class with an empty body whose mro is:
    ``(subclass, T, ABCMeta, type, object)``
    """
