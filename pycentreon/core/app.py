"""
This project is derived from the `PyNetbox` project on 04-2024
Original code avaiable here : https://github.com/netbox-community/pynetbox
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
    gorgone,
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
        "gorgone": gorgone,
        "monitoring": monitoring,
        "platform": platform,
        "users": users,
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