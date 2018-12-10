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

from opsmop.providers.network.network import Network
from opsmop.types.interface import Interface

INTERFACE_FILE_PREFIX = '/etc/sysconfig/network-scripts/ifcfg-{}'
GET_INTERFACE_DETAILS = "cat /etc/sysconfig/network-scripts/ifcfg-{}"
RELOAD_CONFIG = "systemctl restart network"


class SysConfig(Network):

    def plan(self):
        super().plan()

    def apply(self):
        for interface in self.resource.interfaces:
            if self.should('update_interface_{}'.format(interface.name)):
                self.do('update_interface_{}'.format(interface.name))
                self.update_interface(interface)
            elif self.should('create_interface_{}'.format(interface.name)):
                self.do('create_interface_{}'.format(interface.name))
                self.create_interface(interface)
        if self.should('reload_service'):
            self.do('reload_service')
            self.reload_config()
        return self.ok()

    def _generate_options_dict(self, sysconfig_text):
        options_dict = {}
        for line in sysconfig_text.split('\n'):
            if line.startswith("#") or line.strip() == '':
                pass
            else:
                key, value = line.split("=")
                value = value.strip('''\'\"''')  # Get rid of quotes surrounding values
                # Convert 'yes' to True and 'no' to False
                if value.lower() == 'yes':
                    value = True
                elif value.lower() == 'no':
                    value = False
                elif value.isdigit():
                    value = int(value)
                options_dict.update({key: value})
        return options_dict

    def _get_key_map(self):
        """
        This provides a dictionary that maps sysconfig file keys to Interface keys
        :return:
        """
        return {
            'DEVICE': 'name',
            'IPADDR': 'ipv4_address',
            'PREFIX': 'ipv4_prefix',
            'NETMASK': 'ipv4_netmask',
            'GATEWAY': 'ipv4_gateway',
            'METRIC': 'metric',
            'IPV4_FAILURE_FATAL': 'ipv4_failure_fatal',
            'ONBOOT': 'on_boot',
            'BOOTPROTO': 'boot_proto',
            'MTU': 'mtu',
            'DNS': 'dns',
            'MACADDR': 'mac_addr'
        }

    def _get_reverse_map(self):
        """
        This provides a dictionary that maps Interface keys to sysconfig file keys
        :return:
        """
        reverse_key_map = {}
        for k, v in self._get_key_map().items():
            reverse_key_map.update({v: k})
        return reverse_key_map

    def _set_field_values(self, interface_obj, options_dict):
        """
        This sets the field values based on a key mapper (since sysconfig and opsmop have different keys)
        :param interface_obj:
            An interface object instance.

        :param options_dict:
            A dictionary of the current key/value pairs.

        :return:
            None
        """
        key_map = self._get_key_map()
        for k, v in key_map.items():
            if k in options_dict:
                setattr(interface_obj, v, options_dict[k])

    def get_interface_config(self, interface_name):
        # We need to generate an instance of the current state in order to compare the two
        output = self.test(cmd=GET_INTERFACE_DETAILS.format(interface_name))
        if output is None:  # File doesn't exist
            return False  # This will cause the state comparison to fail, triggering the nonexistant file to be created
        try:
            options_dict = self._generate_options_dict(output)
        except ValueError:
            # Parsing failed, nuke the file
            return False
        if 'DEVICE' not in options_dict:
            if 'NAME' in options_dict:
                options_dict.update({'DEVICE': options_dict['NAME']})  # Device and name are effectively duplicates
            return False  # If the DEVICE key isn't present in the config, its a good idea to re-generate it anyways
        # Get a new instance of Interface depending on type
        # TODO: Improve the method used to determine interface type when more types are added
        if 'TYPE' in options_dict:
            if options_dict['TYPE'].lower() == 'ethernet' or 'TYPE' not in options_dict:
                interface_obj = Interface(name=options_dict['DEVICE'])
                self._set_field_values(interface_obj, options_dict)
        else:  # If type isn't specified, its probably an Ethernet device
            interface_obj = Interface(name=options_dict['DEVICE'])
            self._set_field_values(interface_obj, options_dict)
        return interface_obj

    def set_interface_config(self, interface):
        interface_config_lines = []
        for k, v in self._get_reverse_map().items():
            value = getattr(interface, k)
            if value is True:
                value = 'YES'
            elif value is False:
                value = 'NO'
            if value is not None:
                interface_config_lines.append("{k}={v}\n".format(k=v, v=value))
        self.echo(msg="New Interface Config: {}".format("\n".join(interface_config_lines)))
        with open(INTERFACE_FILE_PREFIX.format(interface.name), 'w+') as file:
            file.writelines(interface_config_lines)
        return True

    def create_interface(self, interface):
        return self.set_interface_config(interface)

    def update_interface(self, interface):
        return self.set_interface_config(interface)

    def reload_config(self):
        self.run(RELOAD_CONFIG)


