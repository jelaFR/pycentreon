"""
(c) 2017 DigitalOcean

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
    """The API object is the point of entry to pycentreon.

    After instantiating the Api() with the appropriate named arguments
    you can specify which app and endpoint you wish to interact with.

    Valid attributes currently are:
        * Acknowledgements
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

    Calling any of these attributes will return
    :py:class:`.App` which exposes endpoints as attributes.

    **Additional Attributes**:
        *  **http_session(requests.Session)**:
                Override the default session with your own. This is used to control
                a number of HTTP behaviors such as SSL verification, custom headers,
                retires, and timeouts.
                See `custom sessions <advanced.html#custom-sessions>`__ for more info.

    :param str url: The base URL to the instance of Centreon you
        wish to connect to.
    :param str token: Your Centreon token.
    :param bool,optional threading: Set to True to use threading in ``.all()``
        and ``.filter()`` requests.
    :raises AttributeError: If app doesn't exist.
    :Examples:

    >>> import pycentreon
    >>> nb = pycentreon.api(
    ...     'https://centreon.domain.com/centreon',
    ...     token='d6f4e314a5b5fefd164995169f28ae32d987704f'
    ... )
    """

    def __init__(
        self,
        url,
        token=None,
        threading=False,
    ):
        base_url = "{}/api/latest".format(url if url[-1] != "/" else url[:-1])
        self.token = token
        self.base_url = base_url
        self.http_session = requests.Session()
        self.threading = threading
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
        self.services = App(self, "services")
        self.timeperiods = App(self, "timeperiods")


    def create_token(self, username, password):
        """Creates an API token using a valid Centreon username and password.
        Saves the created token automatically in the API object.

        :Returns: The token as a ``Record`` object.
        :Raises: :py:class:`.RequestError` if the request is not successful.

        :Example:

        >>> import pycentreon
        >>> ctn = pycentreon.api("https://centreon-server")
        >>> token = ctn.create_token("centreon_user", "centreon_password")
        >>> ctn.token
        '96d02e13e3f1fdcd8b4c089094c0191dcb045bef'
        >>> from pprint import pprint
        >>> pprint(dict(token))
            {
            'contact': {
                'alias': 'user',
                'email': 'user@mail.com',
                'id': 1,
                'is_admin': True,
                'name': 'User Name'
                },
            'security': {
                'token': 'centreon_token'
                }
            }
        >>>
        """
        resp = Request(
            base="{}/login".format(self.base_url),
            http_session=self.http_session,
        ).post(data={"security": {"credentials": {"login": username, "password": password}}})
        # Save the newly created API token, otherwise populating the Record
        # object details will fail
        self.token = resp.get("security", []).get("token",None)
        return Record(resp, self, None)