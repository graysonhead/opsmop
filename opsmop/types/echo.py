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

from opsmop.core.field import Field
from opsmop.core.fields import Fields
from opsmop.types.type import Type


class Echo(Type):

    def __init__(self, *args, **kwargs):
        self.setup(**kwargs)

    def quiet(self):
        return True

    def fields(self):
        return Fields(
            self,
            msg = Field(kind=str, allow_none=True, default=None, help="string to print"),
            msg_list = Field(kind=list, allow_none=True, default=None, help="List of strings to print")
        )

    def validate(self):
        pass

    def default_provider(self):
        from opsmop.providers.echo import Echo
        return Echo
