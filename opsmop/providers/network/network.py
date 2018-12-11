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

from opsmop.providers.provider import Provider
from opsmop.core.errors import ValidationError

GET_INTERFACES = "cat /proc/net/dev"


class Network(Provider):

    def get_interface_config(self, interface):
        raise NotImplementedError

    def plan(self):
        valid_interface_names = self._get_valid_interfaces()
        for interface in self.resource.interfaces:
            # First validate that the requested interface exists and raise an error if not
            if interface.name in valid_interface_names:
                current_state = self.get_interface_config(interface.name)
                if current_state.get_fields_dict() and current_state.get_fields_dict() != interface.get_fields_dict():
                    self.needs('update_interface_{}'.format(interface.name))
                elif not current_state:
                    self.needs('create_interface_{}'.format(interface.name))
            else:
                raise ValidationError(msg="Interface {} does not exist".format(interface.name))
        if self.actions_planned.__len__() > 0 and self.auto_reload:
            self.needs('reload_service')

    def _get_valid_interfaces(self):
        valid_interfaces = []
        output = self.test(GET_INTERFACES)
        for line in output.split('\n'):
            if ':' in line:
                valid_interfaces.append(line.split(':')[0].strip())
        return valid_interfaces
