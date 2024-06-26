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

from .gorgone import(
    Pollers
)

from .configuration import(
    Hosts,
    HostsCategories,
    HostsGroups,
    HostsTemplates,
    MetaServices,
    Resources,
    Services,
    ServicesCategories,
    ServicesGroups,
    ServicesTemplates
)

from .monitoring import(
    Hosts,
    HostsCategories,
    HostsGroups,
    HostsTemplates,
    MetaServices,
    Resources,
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
    "configuration.metaservices": MetaServices,
    "configuration.resources": Resources,
    "configuration.services": Services,
    "configuration.services_categories": ServicesCategories,
    "configuration.services_groups": ServicesGroups,
    "configuration.services_severities": None,
    "configuration.services_templates": ServicesTemplates,
    "monitoring.hosts": Hosts,
    "monitoring.hosts_categories": HostsCategories,
    "monitoring.hosts_groups": HostsGroups,
    "monitoring.hosts_severities": None,
    "monitoring.hosts_templates": HostsTemplates,
    "monitoring.metaservices": MetaServices,
    "monitoring.resources": Resources,
    "monitoring.services": Services,
    "monitoring.services_categories": ServicesCategories,
    "monitoring.services_groups": ServicesGroups,
    "monitoring.services_severities": None,
    "monitoring.services_templates": ServicesTemplates,
    "gorgone.pollers": Pollers,
}