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

from .configuration import(
    Hosts,
    HostsCategories,
    HostsGroups,
    HostsTemplates,
    Services,
    ServicesCategories,
    ServicesGroups,
    ServicesTemplates
)

CONTENT_TYPE_MAPPER = {
    "configuration.hosts": Hosts,
    "configuration.hosts_categories": HostsCategories,
    "configuration.hosts_groups": HostsGroups,
    "configuration.hosts_severities": None,
    "configuration.hosts_templates": HostsTemplates,
    "configuration.services": Services,
    "configuration.services_categories": ServicesCategories,
    "configuration.services_groups": ServicesGroups,
    "configuration.services_severities": None,
    "configuration.services_templates": ServicesTemplates,
}