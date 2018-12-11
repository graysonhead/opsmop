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
from opsmop.facts.platform import Platform
from opsmop.types.type import Type
from opsmop.core.errors import ValidationError, NoSuchProviderError


class InterfaceAbstract(Type):
    is_abstract = True


class Interface(InterfaceAbstract):

    def __init__(self, name=None, **kwargs):
        self.setup(name=name, **kwargs)

    def get_fields_dict(self):
        fields = [
            'name',
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
        fields_dict = {}
        for key in fields:
            fields_dict.update({key: getattr(self, key)})
        return fields_dict

    def fields(self):
        return Fields(
            self,
            name=Field(kind=str, default=None, help="The name of the interface"),
            ipv4_address=Field(kind=str, default=None, help="The IPv4 address of the interface"),
            ipv4_prefix=Field(kind=int, default=None, help="Prefix of the IPv4 network (I.E. prefix=24 = ipv4_netmask=255.255.255.0"),
            ipv4_netmask=Field(kind=str, default=None, help="The IPv4 netmask of the interface"),
            ipv4_gateway=Field(kind=str, default=None, help="The IPv4 gateway of the interface"),
            ipv4_failure_fatal=Field(kind=bool, default=False, help="If True, the configuration of the interface will fail if dchlient fails"),
            metric=Field(kind=int, default=None, help="The metric of the interface"),
            on_boot=Field(kind=bool, default=True, help="Controls whether or not the interface is active on boot"),
            # Not Implemented yet hotplug=Field(kind=bool, help="Controls whether or not the interface is hot-pluggable"),
            # Not Implemented yet userctl
            boot_proto=Field(kind=str, default='none', help="Determines if and how an interface gets assigned an address"),
            # VLAN is included in base for sysctl, but we are probably going to move it to a special category
            mtu=Field(kind=int, default=1500, help="Configures interface maximum frame size."),
            # Not Implemented window yet
            # TODO: Process DNS parameter
            dns=Field(kind=list, default=None,
                      help="Accepts up to two DNS servers. Using this option on multiple interfaces in the same "
                           "system may produce unexpected results"),
            # Not Implemented yet scope
            # Not implemented srcaddr
            mac_addr=Field(kind=str, default=None, help="Overrides the mac address of the interface"),
            # Not Implemented nozeroconf
        )

    def _field_str_validator(self, field, allowed_options):
        if field not in allowed_options:
            options = ', '.join(allowed_options)
            raise ValidationError(msg="Field {field} must contain one of the following options {opts}."
                                  .format(field=field, opts=options))

    def validate(self):
        """
        We need to do a few things here:
        validate that any str options contain allowed values
        validate that all IP and MAC addresses are formatted correctly
        ensure that any list with a required length isn't too long (such as DNS)
        :return:
        """

        boot_proto_values = ['none', 'dhcp', 'bootp']
        fields_to_validate = [
            (self.boot_proto, boot_proto_values)
        ]
        for f in fields_to_validate:
            if f[0]:
                self._field_str_validator(f[0], f[1])

        # Validate list lengths
        if self.dns:
            if self.dns.__len__() > 2:
                #TODO: validate that the servers are formatted as proper IP strings
                raise ValidationError(msg="DNS option cannot contain more than two dns servers")
            #TODO: Validate MAC addresses
            #TODO: Validate IP addresses
