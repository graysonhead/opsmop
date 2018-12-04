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

import socket
import fcntl
import struct

from opsmop.facts.facts import Facts

SIOCGIFADDR = 0x8915  # IP Address
SIOCGIFBRDADDR = 0x8919  # Broadcast Address


class NetInterfacesFacts(Facts):

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def _get_input_buffer(self, ifname):
        return struct.pack('256s', bytes(ifname, 'utf-8'))

    def interface_ipv4_address(self, ifname):
        buffer = fcntl.ioctl(self.sock.fileno(), SIOCGIFADDR, self._get_input_buffer(ifname))
        return socket.inet_ntoa(buffer[20:24])
