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
from pycentreon.models import(
    acknowledgements,
    administration,
    command,
    contacts,
    downtimes,
    gorgone,
    host,
    monitoring_servers,
    notification,
    platform,
    proxy,
    service,
    timeperiods
)

class App:
    """Represent apps in Centreon
    """

    def __init__(self, api, name):
        self.api = api
        self.name = name
        self._setmodel()

    models = {
        "acknowledgements": acknowledgements,
        "administration": administration,
        "command": command,
        "contacts": contacts,
        "downtimes": downtimes,
        "gorgone": gorgone,
        "host": host,
        "monitoring-servers": monitoring_servers,
        "notification": notification,
        "platform": platform,
        "proxy": proxy,
        "service": service,
        "timeperiods": timeperiods
    }

    def _setmodel(self):
        self.model = App.models[self.name] if self.name in App.models else None

    def config(self):
        config = Request(
            base="{}/{}/configuration/".format(
                self.api.base_url,
                self.name,
            ),
            token=self.api.token,
            http_session=self.api.http_session,
        ).get()
        return config
