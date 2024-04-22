"""
General core structure:
-----------------------
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
from pycentreon.core.endpoint import Endpoint
from pycentreon.core.query import Request
from pycentreon.models import (
    administration,
    configuration,
    monitoring,
    platform,
    users
)


class App:
    """Represents apps in Centreon.

    Calls to attributes are returned as Endpoint objects.

    :returns: :py:class:`.Endpoint` matching requested attribute.
    :raises: :py:class:`.RequestError`
        if requested endpoint doesn't exist.
    """

    def __init__(self, api, name):
        self.api = api
        self.name = name
        self._setmodel()

    models = {
        "administration": administration,
        "configuration": configuration,
        "monitoring": monitoring,
        "platform": platform,
        "users": users
    }

    def _setmodel(self):
        self.model = App.models[self.name] if self.name in App.models else None

    def __getstate__(self):
        return {"api": self.api, "name": self.name}

    def __setstate__(self, d):
        self.__dict__.update(d)
        self._setmodel()

    def __getattr__(self, name):
        return Endpoint(self.api, self, name, model=self.model)

    def config(self):
        """Returns config response from app

        :Returns: Raw response from Centreon's config endpoint.
        :Raises: :py:class:`.RequestError` if called for an invalid endpoint.
        :Example:

        #TODO : Pur a representation of config result
        >>> pprint.pprint(
        """
        config = Request(
            base="{}/monitoring/{}".format(
                self.api.base_url,
                self.name,
            ),
            token=self.api.token,
            http_session=self.api.http_session,
        ).get()
        return config