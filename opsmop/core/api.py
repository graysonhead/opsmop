# Copyright 2018 Michael DeHaan LLC, <michael@michaeldehaan.net>
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from runpy import run_path

from opsmop.core.executor import Executor

class Api(object):


    __slots__ = [ '_policies', '_tags' ]

    def __init__(self, policies=None, tags=None):

        assert type(policies) == list
        self._policies = policies
        self._tags = tags

    @classmethod
    def from_file(cls, path=None, tags=None):

        assert path is not None

        path = os.path.abspath(os.path.expandvars(os.path.expanduser(path)))
        
        if not os.path.exists(path):
            raise Exception("file does not exist: %s" % path)

        dirname = os.path.dirname(path)
        os.chdir(dirname)
        ran = run_path(path)

        if 'main' not in ran:
            raise Exception("unable to find main() function in %s" % path)
        policies = ran['main']()
        if type(policies) != list:
            policies = [ policies ]

        return cls(policies=policies, tags=tags)
        
    def validate(self):
        """
        This just checks for invalid types in the python file as well as missing files
        and non-sensical option combinations.
        """
        executor = Executor(policies=self._policies, tags=self._tags)
        contexts = executor.validate()
        return contexts

    def check(self):
        """
        This is dry-run mode
        """
        executor = Executor(policies=self._policies, tags=self._tags)
        contexts = executor.check()
        return contexts

    def apply(self):
        """
        This is live-configuration mode.
        """
        executor = Executor(policies=self._policies, tags=self._tags)
        contexts = executor.apply()
        return contexts
