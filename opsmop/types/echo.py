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
from opsmop.core.errors import ValidationError


class Echo(Type):

    def __init__(self, *args, **kwargs):
        self.setup(**kwargs)

    def quiet(self):
        return True

    def fields(self):
        return Fields(
            self,
            msg = Field(allow_none=False, help="String, or list of strings to print"),
        )

    def validate(self):
        # Make sure that msg is either a list or string
        if type(self.msg) not in [list, str]:
            raise ValidationError(msg="msg parameter must contain either a string or list of strings.")
        # If its a list, make sure the list contains only strings
        elif type(self.msg) is str:
            if not all(map(lambda x: isinstance(x, str), self.msg)):
                raise ValidationError(msg="msg list must contain only strings.")

    def default_provider(self):
        from opsmop.providers.echo import Echo
        return Echo
