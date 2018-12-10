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
from opsmop.core.errors import ValidationError
from opsmop.facts.platform import Platform


class Interfaces(Type):

    def __init__(self, *interfaces, **kwargs):
        self.setup(**kwargs)
        self.interfaces = list(interfaces)

    def fields(self):
        return Fields(
            self,
            auto_reload=Field(kind=bool,
                              default=False,
                              help="Auto reloads the networking service if changes are made. Default: False"),
            force=Field(kind=bool,
                        default=False,
                        help="Overwrite configuration even if the original file cannot be parsed.")
            )

    def add(self, interface):
        """
        Adds interface(s) to the resource
        """
        if isinstance(interface, Interface):
            self.interfaces.append(interface)
        elif isinstance(interface, list):
            for interf in interface:
                if isinstance(interf, Interface):
                    self.interfaces.append(interf)
                else:
                    raise ValidationError(msg="You can only add interface objects to an interfaces type")
        else:
            raise ValidationError(msg="You can only add interface objects to an interfaces type")

    def get_provider(self, method):
        if method == 'sysconfig':
            from opsmop.providers.network.sysconfig import SysConfig
            return SysConfig

    def default_provider(self):
        return Platform.default_network_manager()

    def validate(self):
        for interface in self.interfaces:
            interface.validate()
