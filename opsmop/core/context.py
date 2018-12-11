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

HOST = None
HOST_SIGNALS = dict()
MODE = None

VALIDATE = 'validate'
CHECK = 'check'
APPLY = 'apply'

class Context(object):

    @classmethod
    def set_mode(cls, mode):
        global MODE
        assert mode in [ VALIDATE, CHECK, APPLY ]
        MODE = mode

    @classmethod
    def set_host(cls, host):
        global HOST
        HOST = host

    @classmethod
    def host(cls):
        return host

    @classmethod
    def mode(cls):
        global MODE
        return MODE

    @classmethod
    def is_validate(cls):
        return MODE == VALIDATE

    @classmethod
    def is_check(cls):
        return MODE == CHECK

    @classmethod
    def is_apply(cls):
        return MODE == APPLY

    @classmethod
    def add_signal(cls, host, signal):

        global HOST_SIGNALS
        if not host.name in HOST_SIGNALS:
            HOST_SIGNALS[host.name] = []
        HOST_SIGNALS[host.name].append(signal)

    @classmethod
    def has_seen_any_signal(cls, host, signals):

        global HOST_SIGNALS
        host_signals = HOST_SIGNALS.get(host.name, [])

        for x in host_signals:
            if x in signals:
                return True
        return False
   