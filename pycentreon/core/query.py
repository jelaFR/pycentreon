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

import json
import urllib3

class RequestError(Exception):
    def __init__(self, req):
        if req.status_code == 404:
            self.message = "The requested url: {} could not be found.".format(req.url)
        else:
            try:
                self.message = "The request failed with code {} {}: {}".format(
                    req.status_code, req.reason, req.json()
                )
            except ValueError:
                self.message = (
                    "The request failed with code {} {} but more specific "
                    "details were not returned in json.".format(
                        req.status_code, req.reason
                    )
                )

        super().__init__(self.message)
        self.req = req
        self.request_body = req.request.body
        self.base = req.url
        self.error = req.text

    def __str__(self):
        return self.message


class AllocationError(Exception):
    def __init__(self, req):
        super().__init__(req)
        self.req = req
        self.request_body = req.request.body
        self.base = req.url
        self.error = "The requested allocation could not be fulfilled."

    def __str__(self):
        return self.error


class ContentError(Exception):
    def __init__(self, req):
        super().__init__(req)
        self.req = req
        self.request_body = req.request.body
        self.base = req.url
        self.error = (
            "The server returned invalid (non-json) data."
        )

    def __str__(self):
        return self.error


class Request:
    """Creates requests to the centreon API

    This is where the API request is made through the requests python library

    :param base: (str) Centreon Base URL passed to the Api()
    :param token: (str) Token passed to requests to make api call
    :param http_session: Requests ``Session()``used to maintain http session
    :param ca_verify: Validate SSL certificate to check Centreon server identity

    """

    def __init__(self, base, http_session, token=None, ca_verify=False):
        self.url = self.normalize_url(base)
        self.token = token
        self.http_session = http_session
        self.ca_verify = ca_verify

    def get_status(self):
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["X-AUTH-TOKEN"] = "{}".format(self.token)
        req = self.http_session.get(
            "{}status/".format(self.normalize_url(self.base)),
            headers=headers,
        )
        if req.ok:
            return req.json()
        else:
            raise RequestError(req)


    def normalize_url(self, url):
        # FIX: Centreon is unable to get token if using /login/ URL
        if (url[-1] != "/") and ("login" not in url):
            return "{}/".format(url)

        return url
    
    def _make_call(self, action="get", data=None, add_params=None, search=None, limit=None):
        if action in ("post", "put") or action == "delete" and data:
            headers = {"Content-Type": "application/json"}
        else:
            headers = {"accept": "application/json"}

        if self.token:
            headers["X-AUTH-TOKEN"] = "{}".format(self.token)
        params = {}

        if self.ca_verify == False:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        req = getattr(self.http_session, action)(
            self.url, headers=headers, params=params, json=data, verify=self.ca_verify
        )

        # Results
        if action == "delete":
            if req.ok:
                return True
            else:
                raise RequestError(req)
        elif req.ok:
            try:
                return req.json()
            except json.JSONDecodeError:
                try:
                    return req.text
                except:
                    raise ContentError(req)
        else:
            raise RequestError(req)

    def get(self, add_params=None):
        req = self._make_call(action="get")
        if isinstance(req, dict) and req.get("results") is not None:
            pass
        elif isinstance(req, list):
            pass
        yield req

    def patch(self, data):
        return self._make_call(verb="patch", data=data)

    def put(self, data):
        return self._make_call(verb="put", data=data)

    def post(self, data):
        return self._make_call(action="post", data=data)
    
    def delete(self, data):
        return self._make_call(action="delete", data=data)
    
    def options(self):
        return self._make_call(verb="options")