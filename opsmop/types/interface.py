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
from opsmop.core.resource import Resource
from opsmop.core.errors import ValidationError, NoSuchProviderError
from ipaddress import IPv4Address, AddressValueError

NETWORK_FIELDS = [
            'device',
            'ipv4_address',
            'ipv4_prefix',
            'ipv4_netmask',
            'ipv4_gateway',
            'ipv4_failure_fatal',
            'metric',
            'on_boot',
            'boot_proto',
            'mtu',
            'dns',
            'mac_addr'
        ]
ALLOWED_BOOT_PROTO_VALUES = ['none', 'dhcp', 'bootp']


class Interface(Resource):

    def __init__(self, device=None, **kwargs):
        self.setup(device=device, **kwargs)

    def __eq__(self, other):
        return all(getattr(self, key) == getattr(other, key) for key in NETWORK_FIELDS)

    def fields(self):
        return Fields(
            self,
            device=Field(kind=str, default=None, help="Name of physical devicelogical name"),
            ipv4_address=Field(kind=str, default=None, help="IPv4 address of the interface("),
            ipv4_prefix=Field(kind=int, default=None, help="Prefix of the IPv4 network "
                                                           "(ex: prefix=24 == ipv4_netmask=255.255.255.0)"),
            ipv4_netmask=Field(kind=str, default=None, help="IPv4 netmask of the interface "
                                                            "(ex: ipv4_netmask=255.255.255.0 == prefix=24)"),
            ipv4_gateway=Field(kind=str, default=None, help="IPv4 gateway of the interface"),
            ipv4_failure_fatal=Field(kind=bool, default=False, help="If True, the configuration of the "
                                                                    "interface will fail if dchlient fails"),
            metric=Field(kind=int, default=None, help="The metric of the interface"),
            on_boot=Field(kind=bool, default=True, help="Controls whether or not the interface is active on boot"),
            boot_proto=Field(kind=str,
                             default='none',
                             help="'bootp' or 'dhcp' cause a DHCP client to run on the device."
                                  " Any other value causes any static configuration in the file to be applied."),
            mtu=Field(kind=int, default=1500, help="Configures interface maximum frame size in bytes."),
            # TODO: Process DNS parameter
            dns=Field(kind=list, default=None,
                      help="Accepts up to two DNS servers. Using this option on multiple interfaces in the same "
                           "system may produce unexpected results"),
            mac_addr=Field(kind=str,
                           default=None,
                           help="Ethernet hardware address for this device, ex: 'AA:BB:CC:DD:EE:FF'"),
        )

    def _field_str_validator(self, field, allowed_options):
        if field not in allowed_options:
            options = ', '.join(allowed_options)
            raise ValidationError(msg=f"Field {field} must contain one of the following options {options}.")

    def validate(self):
        """
        We need to do a few things here:
        validate that any str options contain allowed values
        validate that all IP and MAC addresses are formatted correctly
        ensure that any list with a required length isn't too long (such as DNS)
        """

        fields_to_validate = [
            (self.boot_proto, ALLOWED_BOOT_PROTO_VALUES)
        ]
        for f in fields_to_validate:
            if f[0]:
                self._field_str_validator(f[0], f[1])

        # Validate list lengths
        if self.dns:
            if self.dns.__len__() > 2:
                #TODO: validate that the servers are formatted as proper IP strings
                raise ValidationError(msg="DNS option cannot contain more than two dns servers")
            for server in self.dns:
                try:
                    IPv4Address(server)
                except AddressValueError as e:
                    raise ValidationError(msg=f'DNS validation failed {server} is not a valid IP address: {e}')
        #TODO: Validate MAC addresses
        #TODO: Validate IP addresses
        if self.ipv4_address:
            try:
                IPv4Address(self.ipv4_address)
            except AddressValueError as e:
                raise ValidationError(msg=f'Interface {self.device} failed validation: {e}')
