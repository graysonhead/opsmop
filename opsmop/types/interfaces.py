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
from opsmop.types.interface import Interface
from opsmop.types.type import Type


class Interfaces(Type):

    def __init__(self, **kwargs):
        self.setup(**kwargs)
        self.interfaces = []

    def fields(self):
        return Fields(
            self,
            auto_reload=Field(kind=bool, default=True, help="Auto reloads the networking service ")
            )

    def add(self, interface):
        if isinstance(interface, Interface):
            self.interfaces.append(interface)
        elif isinstance(interface, list):
            for interf in interface:
                self.interfaces.append(interf)

    def get_provider(self, method):
        if method == 'sysconfig':
            from opsmop.providers.network.sysconfig import SysConfig
            return SysConfig

    def default_provider(self):
        # TODO: platform facts for default providers
        pass