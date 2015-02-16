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
from metautils.compat import reduce


def compose(*args, _apply_=lambda a, b: b(a)):
    """
    Compose functions.
    """
    # _apply_ is defined as a default argument so that we do not need to
    # construct a new function everytime this is called, and so that
    # we do not need to resolve the name out of the globals.
    def composed(base):
        return reduce(_apply_, reversed(args), base)

    return composed
