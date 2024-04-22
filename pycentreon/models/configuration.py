"""
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from pycentreon.core.query import Request
from pycentreon.core.response import Record, JsonField
from pycentreon.core.endpoint import RODetailEndpoint, DetailEndpoint

class DeviceTypes(Record):
    def __str__(self):
        return self.model

## Host class

class Hosts(Record):
  pass

class HostsGroups(Record):
  pass

class HostsCategories(Record):
  pass

class HostsTemplates(Record):
  pass

## Services class

class Services(Record):
  pass

class ServicesGroups(Record):
  pass

class ServicesCategories(Record):
  pass

class ServicesTemplates(Record):
  pass