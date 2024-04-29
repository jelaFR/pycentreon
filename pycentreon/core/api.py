"""
This project is derived from the `PyNetbox` project on 04-2024
Original code avaiable here : https://github.com/netbox-community/pynetbox
(c) 2017 DigitalOcean

Licensed under the Apache Licsense, Version 2.0 (the "License");
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
    """The API object is the point of entry to pynetbox.

    After instantiating the Api() with the appropriate named arguments
    you can specify which app and endpoint you wish to interact with.

    Valid attributes currently are:
        * administration
        * configuration
        * gorgone
        * monitoring
        * platform
        * users

    Calling any of these attributes will return
    :py:class:`.App` which exposes endpoints as attributes.

        **Additional Attributes**:
        *  **http_session(requests.Session)**:
                Override the default session with your own. This is used to control
                a number of HTTP behaviors such as SSL verification, custom headers,
                retires, and timeouts.
                See `custom sessions <advanced.html#custom-sessions>`__ for more info.

    :param str url: Centreon base URL (with the ending /centreon)
    :param str token: Your NetBox token.
    :raises AttributeError: If app doesn't exist.


    :Examples:

    Using SSL certificates signed with with public CA:

    >>> import pycentreon
    >>> ctn = pycentreon.api(
    ...     'https://centreon.example.com/centreon',
    ...     token='centreon_token_value'
    ... )
    >>> print(list(ctn.monitoring.hosts.all()))
    >>> [host1, host2, host3]

    Using certificates signed with private CA with SSL verification:

    >>> import pycentreon
    >>> import os
    >>> os.environ['REQUESTS_CA_BUNDLE'] = "ca_cert.pem"
    >>> ctn = pycentreon.api(
    ...     'https://centreon.example.com/centreon',
    ...     token='centreon_token_value'
    ... )
    >>> print(list(ctn.monitoring.hosts.all()))
    >>> [host1, host2, host3]
    """
    def __init__(
        self,
        url,
        token=None,
    ):            
        # Centreon httpd uses the following regexp to redirect to Centreon API
        #   ^\${base_uri}/?(?!api/latest/|api/beta/|api/v[0-9]+/|api/v[0-9]+\.[0-9]+/)(.*\.php(/.*)?)$
        base_url = "{}/api/latest".format(url if url[-1] != "/" else url[:-1])
        self.token = token
        self.base_url = base_url
        self.http_session = requests.Session()
        self.administration = App(self, "administration")
        self.configuration = App(self, "configuration")
        self.gorgone = App(self, "gorgone")
        self.monitoring = App(self, "monitoring")
        self.platform = App(self, "platform")
        self.users = App(self, "users")

    def create_token(self, username, password):
        """Create an API token for Centreon API v2
        Saves the created token automatically in the API object.

        This requires the following parameters to be set:
            >> Configuration > Users > Contact/Users
            -- Centreon Authentication
            ---- Reach API Configuration : Yes
            ---- Reach API Realtime : Yes

        :Returns: The token as a ``Record`` object.
        :Raises: :py:class:`.RequestError` if the request is not successful.

        :Examples:
        >>> import pycentreon
        >>> centreon_login = "api_admin"
        >>> centreon_password = "api_password"
        >>> ctn = pycentreon.api('https://centreon.example.com/centreon')
        >>> ctn.create_token(centreon_login, centreon_password)
        >>> print(f"Centreon token: {ctn.token}")

        >>> Centreon token: V4olz/ogbqD8xmeqUfdfdfdfdfdfS7p/qThnE/FBi75DjXKII7r8bzzze
        """
        resp = Request(
            base="{}/login".format(self.base_url),
            http_session=self.http_session,
        ).post(data={"security": {"credentials": {"login": username, "password": password}}})
        # Save the newly created API token, otherwise populating the Record
        # object details will fail
        self.token = resp.get("security", []).get("token",None)
        return Record(resp, self, None)
    
    def delete_token(self):
        """ Invalidates existing Centreon API v2 token.

        :Examples:
        >>> import pycentreon
        >>> cnt = pycentreon.api(
        ...     'https://centreon.example.com/centreon',
        ...     token='centreon_token_value'
        ... )
        >>> cnt.logout()
        """
        resp = Request(base="{}/logout".format(self.base_url), http_session=self.http_session).get()
        return Record(resp, self, None)