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

# This provider method works with RHEL derivatives (CentOS 6 and newer) that use the network service

from opsmop.providers.network.network import LinuxNetwork
from opsmop.types.interface import Interface

INTERFACE_FILE_PREFIX = '/etc/sysconfig/network-scripts/ifcfg-{}'
GET_INTERFACE_DETAILS = "cat /etc/sysconfig/network-scripts/ifcfg-{}"
RELOAD_CONFIG = "systemctl restart network"
GET_INTERFACES = "cat /proc/net/dev"

KEY_MAP = {
            'DEVICE': 'device',
            'IPADDR': 'ipv4_address',
            'PREFIX': 'ipv4_prefix',
            'NETMASK': 'ipv4_netmask',
            'GATEWAY': 'ipv4_gateway',
            'METRIC': 'metric',
            'IPV4_FAILURE_FATAL': 'ipv4_failure_fatal',
            'ONBOOT': 'on_boot',
            'BOOTPROTO': 'boot_proto',
            'MTU': 'mtu',
            'MACADDR': 'mac_addr'
        }

class SysConfig(LinuxNetwork):

    def plan(self):
        super().plan()

    def apply(self):
        for interface in self.resource.interfaces:
            if self.should('update_interface_{}'.format(interface.device)):
                self.do('update_interface_{}'.format(interface.device))
                self.update_interface(interface)
            elif self.should('create_interface_{}'.format(interface.device)):
                self.do('create_interface_{}'.format(interface.device))
                self.create_interface(interface)
        if self.should('reload_service'):
            self.do('reload_service')
            self.reload_config()
        return self.ok()

    def _options_from_config(self, sysconfig_text):
        """
        Parses a sysconfig text file and returns a dictionary of the keys and values
        Ex:
       {
            'DEVICE': 'ens9',
            'IPADDR': '10.1.1.143',
            'NETMASK': '255.255.255.0',
            'METRIC': 2,
            'IPV4_FAILURE_FATAL': False,
            'ONBOOT': True,
            'BOOTPROTO': 'static',
            'MTU': 2300
        }
        """
        options = {}
        for line in sysconfig_text.splitlines():
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
                options.update({key: value})
        return options

    def _get_reverse_map(self):
        """
        This provides a dictionary that maps Interface keys to sysconfig file keys
        """
        return {v: k for k, v in KEY_MAP.items()}

    def _populate_interface_attributes_from_file(self, interface_obj, options_dict):
        """
        This sets the field values based on a key mapper (since sysconfig and opsmop have different keys)
        """
        for (k, v) in KEY_MAP.items():
            if k in options_dict:
                setattr(interface_obj, v, options_dict[k])
        if 'DNS1' or 'DNS2' in options_dict:
            interface_obj.dns = []
            if 'DNS1' in options_dict:
                interface_obj.dns.append(options_dict['DNS1'])
            if 'DNS2' in options_dict:
                interface_obj.dns.append(options_dict['DNS2'])

    def get_interface_config(self, interface_device):
        """
        This method accepts a string containing the name of the interface device to fetch, and then
        runs all necesarry methods to collect information about it, parse it, and return it as an Interface Object
        """
        # We need to generate an instance of the current state in order to compare the two
        output = self.test(cmd=GET_INTERFACE_DETAILS.format(interface_device))
        # File doesn't exist
        if output is None:
            # This will cause the state comparison to fail, triggering the nonexistant file to be created
            return False
        try:
            options = self._options_from_config(output)
        except ValueError:
            if self.force:
                return False
            else:
                self.error(f"The interfaces file for {interface_device} could not be read,"
                f" add the 'force' parameter to your Interfaces resource to overwrite it anyways.")
        # Ensure that DEVICE is present, if there is no DEVICE try to use the name
        if 'DEVICE' not in options:
                return False
        # Get a new instance of Interface depending on type
        # TODO: Improve the method used to determine interface type when more types are added
        if 'TYPE' in options:
            if options['TYPE'].lower() == 'ethernet':
                interface_obj = Interface(device=options['DEVICE'])
                self._populate_interface_attributes_from_file(interface_obj, options)
            else:
                self.error(f"The type {options['TYPE']} is not currently supported by this module")
        # If type isn't specified, its probably an Ethernet device
        else:
            interface_obj = Interface(device=options['DEVICE'])
            self._populate_interface_attributes_from_file(interface_obj, options)
        return interface_obj

    def _get_interfaces(self):
        """
        This returns a list of interfaces present on the system
        """
        valid_interfaces = {}
        output = self.test(GET_INTERFACES)
        for line in output.split('\n'):
            if ':' in line:
                if_name = line.split(':')[0].strip()
                valid_interfaces.update({if_name: self.get_interface_config(if_name)})
        return valid_interfaces

    def set_interface_config(self, interface):
        """
        This generates an ifcfg-{devname} file and writes it to the filesystem of the machine
        """
        interface_config_lines = []
        # This gets the reverse of the key map specified above to map OpsMop keys to sysconfig keys
        for k, mapped_key in self._get_reverse_map().items():
            value = getattr(interface, k)
            # True and False map to "YES" and "NO" in sysconfig files
            if value is True:
                value = 'YES'
            elif value is False:
                value = 'NO'
            if value is not None:
                interface_config_lines.append(f"{mapped_key}={value}\n")
        # DNS servers are a special case, since it accepts a list as a parameter
        if interface.dns:
            # Sysconfig can only accept two DNS servers at most
            for idx, srv in enumerate(interface.dns[0:2]):
                interface_config_lines.append(f"DNS{idx + 1}={srv}\n")
        self.echo(msg="New Interface Config:")
        for line in interface_config_lines:
            self.echo(msg=line.strip('\n'))
        with open(INTERFACE_FILE_PREFIX.format(interface.device), 'w+') as file:
            file.writelines(interface_config_lines)
        return True

    def create_interface(self, interface):
        """Wrapper for when we are making an interface"""
        return self.set_interface_config(interface)

    def update_interface(self, interface):
        """Wrapper for when we are updating an interface"""
        return self.set_interface_config(interface)

    def reload_config(self):
        """Reload the systemctl config"""
        self.run(RELOAD_CONFIG)


