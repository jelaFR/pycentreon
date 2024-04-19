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

import requests

from pycentreon.core.query import Request
from pycentreon.core.app import App
from pycentreon.core.response import Record

class Api:
    """This object is the entry point to centreon_sdk.

    You have to instantiate the Api() object in order to interract
    with the following objects:
        * Acknowlegements
        * Administration
        * Command
        * Contacts
        * Downtimes
        * Gorgone
        * Host
        * Monitoring-servers
        * Notification
        * Platform
        * Proxy
        * Service
        * Timeperiods

    :param str url: Base URL for Centreon instance
    :param str token: Centreon Token if you already have one
    :Examples:

        *Connect without token
            >> import pycentreon
            >> username = "api_user"
            >> password = "api_password"
            >> cnt = pycentreon.api('https://192.0.2.2/centreon')
            >> cnt.create_token(username, password)

        * Connect with token
            >> import pycentreon
            >> token = "centreon_token"
            >> cnt = pycentreon.api('https://192.0.2.2/centreon', token)

    """

    def __init__(self, url, token=None):
        base_url = "{}/api/latest".format(url if url[-1] != "/" else url[:-1])
        self.token = token
        self.base_url = base_url
        self.http_session = requests.Session()

        # Instantiate models
        self.acknowledgements = App(self, "acknowledgements")
        self.administration = App(self, "administration")
        self.command = App(self, "command")
        self.contacts = App(self, "contacts")
        self.downtimes = App(self, "downtimes")
        self.gorgone = App(self, "gorgone")
        self.hosts = App(self, "hosts")
        self.monitoring_servers = App(self, "monitoring_servers")
        self.notification = App(self, "notification")
        self.platform = App(self, "platform")
        self.proxy = App(self, "proxy")
        self.servers = App(self, "servers")
        self.service = App(self, "service")
        self.timeperiods = App(self, "timeperiods")

    def create_token(self, username, password):
        """"Creates an API token using a valid Centreon username and password.
        Saves the created token automatically in the API object.
        
        :Returns: The token as a ``Record`` object.
        """

        auth_credentials = {
        "security": {
            "credentials": {
            "login": username,
            "password": password
            }
        }
        }

        resp = Request(
            base="{}/login".format(self.base_url),
            http_session=self.http_session
        ).post(data=auth_credentials)

        self.token = resp.get("security", []).get("token",None)

        return Record(resp, self)