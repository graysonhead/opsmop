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
from opsmop.core.errors import ProviderError



class LinuxNetwork(Provider):

    def get_interface_config(self, interface):
        """
        This method should return an interface type when run. Make sure you override this
        in your method's class if you are extending this provider
        """
        raise ProviderError

    def get_interfaces(self):
        """
        TODO: This method should return a dict with the current interfaces available on the system
        it is keyed by the device name of the interfaces

        Ex: {'eth0': Interface: ens9}
        """
        raise ProviderError

    def plan(self):
        current_interfaces = self._get_interfaces()
        for interface in self.resource.interfaces:
            # First validate that the requested interface exists and raise an error if not
            if interface.device in current_interfaces:
                current_state = current_interfaces[interface.device]
                if not current_state:
                    self.needs('create_interface_{}'.format(interface.device))
                elif current_state != interface:
                        self.needs('update_interface_{}'.format(interface.device))
            else:
                raise ProviderError(msg="Interface {} does not exist".format(interface.device))
        if len(self.actions_planned) > 0 and self.auto_reload:
            self.needs('reload_service')


