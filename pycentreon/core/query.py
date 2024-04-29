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
import concurrent.futures as cf
import json
from packaging import version


class RequestError(Exception):
    """Basic Request Exception

    More detailed exception that returns the original requests object
    for inspection. Along with some attributes with specific details
    from the requests object. If return is json we decode and add it
    to the message.

    :Example:

    >>> try:
    ...   nb.dcim.devices.create(name="destined-for-failure")
    ... except pynetbox.RequestError as e:
    ...   print(e.error)

    """

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
                    "details were not returned in json. Check the NetBox Logs "
                    "or investigate this exception's error attribute.".format(
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
    """Allocation Exception

    Used with available-ips/available-prefixes when there is no
    room for allocation and NetBox returns 409 Conflict.
    """

    def __init__(self, req):
        super().__init__(req)
        self.req = req
        self.request_body = req.request.body
        self.base = req.url
        self.error = "The requested allocation could not be fulfilled."

    def __str__(self):
        return self.error


class ContentError(Exception):
    """Content Exception

    If the API URL does not point to a valid NetBox API, the server may
    return a valid response code, but the content is not json. This
    exception is raised in those cases.
    """

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
    def __init__(
        self,
        base,
        http_session,
        filters=None,
        limit=None,
        page=None,
        sort_by=None,
        key=None,
        token=None,
    ):
        """_summary_

        Args:
            base (_type_): _description_
            http_session (_type_): _description_
            filters (_type_, optional): _description_. Defaults to None.
            limit (_type_, optional): _description_. Defaults to None.
            page (_type_, optional): _description_. Defaults to None.
            sort_by (_type_, optional): _description_. Defaults to None.
            key (_type_, optional): _description_. Defaults to None.
            token (_type_, optional): _description_. Defaults to None.
        """
        self.base = self.normalize_url(base)
        self.filters = filters or None
        self.key = key
        self.token = token
        self.http_session = http_session
        self.url = self.base if not key else "{}/{}".format(self.base, key)
        self.limit = limit
        self.page = page
        self.sort_by = sort_by

    def normalize_url(self, url):
        """Builds a url for POST actions."""
        if url[-1] == "/":
            return "{}".format(url[:-1])

        return url

    def _make_call(self, verb="get", url_override=None, add_params=None, data=None):
        if verb in ("post", "put") or verb == "delete" and data:
            headers = {"Content-Type": "application/json"}
        else:
            headers = {"accept": "application/json"}

        if self.token:
            headers["X-AUTH-TOKEN"] = "{}".format(self.token)

        params = {}
        if not url_override:
            if self.filters:
                params.update(self.filters)
            if add_params:
                params.update(add_params)

        req = getattr(self.http_session, verb)(
            url_override or self.url, headers=headers, params=params, json=data
        )

        if req.status_code == 409 and verb == "post":
            raise AllocationError(req)
        if verb == "delete":
            if req.ok:
                return True
            else:
                raise RequestError(req)
        elif req.ok:
            try:
                return req.json()
            except json.JSONDecodeError:
                raise ContentError(req)
        else:
            raise RequestError(req)

    def get(self, add_params=None):
        if not add_params and ((self.limit is not None) or (self.page is not None)):
            add_params = {}
            if (self.limit is not None) and isinstance(self.limit,str):
                add_params["limit"] = self.limit
            else: # Set to default => 10 result per page
                add_params["limit"] = "10"
            if self.page is not None and isinstance(self.page,str):
                add_params["page"] = self.page
        req = self._make_call(add_params=add_params)

        if isinstance(req, dict) and req.get("result") is not None:
            self.count = req["meta"]["total"] # Get total object list
            if add_params:
                # only yield requested results until limit
                for i in req["result"]:
                    yield i
            else:
                # yield all results
                add_params = {"limit": self.count}
                req = self._make_call(add_params=add_params)
                for i in req["result"]:
                    yield i
        elif isinstance(req, list):
            self.count = len(req)
            for i in req:
                yield i
        else:
            self.count = len(req)
            yield req

    def put(self, data):
        """Makes PUT request.

        Makes a PUT request to NetBox's API.

        :param data: (dict) Contains a dict that will be turned into a
            json object and sent to the API.
        :raises: RequestError if req.ok returns false.
        :raises: ContentError if response is not json.
        :returns: Dict containing the response from NetBox's API.
        """
        return self._make_call(verb="put", data=data)

    def post(self, data):
        """Makes POST request.

        Makes a POST request to NetBox's API.

        :param data: (dict) Contains a dict that will be turned into a
            json object and sent to the API.
        :raises: RequestError if req.ok returns false.
        :raises: AllocationError if req.status_code is 409 (Conflict)
            as with host / service already existing
        :raises: ContentError if response is not json.
        :Returns: Dict containing the response from NetBox's API.
        """
        return self._make_call(verb="post", data=data)

    def delete(self, data=None):
        """Makes DELETE request.

        Makes a DELETE request to NetBox's API.

        :param data: (list) Contains a dict that will be turned into a
            json object and sent to the API.
        Returns:
            True if successful.

        Raises:
            RequestError if req.ok doesn't return True.
        """
        return self._make_call(verb="delete", data=data)

    def patch(self, data):
        """Makes PATCH request.

        Makes a PATCH request to NetBox's API.

        :param data: (dict) Contains a dict that will be turned into a
            json object and sent to the API.
        :raises: RequestError if req.ok returns false.
        :raises: ContentError if response is not json.
        :returns: Dict containing the response from NetBox's API.
        """
        return self._make_call(verb="patch", data=data)

    def options(self):
        """Makes an OPTIONS request.

        Makes an OPTIONS request to NetBox's API.

        :raises: RequestError if req.ok returns false.
        :raises: ContentError if response is not json.

        :returns: Dict containing the response from NetBox's API.
        """
        return self._make_call(verb="options")

    def get_count(self, *args, **kwargs):
        """Returns object count for query

        Makes a query to the endpoint with ``limit=1`` set and only
        returns the value of the "count" field.

        :raises: RequestError if req.ok returns false.
        :raises: ContentError if response is not json.

        :returns: Int of number of objects query returned.
        """

        if not hasattr(self, "count"):
            self.count = self._make_call(add_params={"limit": 0})["meta"].get("total", 0)
        return self.count
