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
from pycentreon.core.query import Request, RequestError
from pycentreon.core.response import Record, RecordSet

RESERVED_KWARGS = ()


class Endpoint:
    """Represent actions available on endpoints in the Centreon API v2.

    Takes ``name`` and ``app`` passed from App() and builds the correct
    url to make queries to and the proper Response object to return
    results in.

    :arg obj api: Takes :py:class:`.Api` created at instantiation.
    :arg obj app: Takes :py:class:`.App`.
    :arg str name: Name of endpoint passed to App().
    :arg obj,optional model: Custom model for given app.

    """
    def __init__(self, api, app, name, model=None):
        self.return_obj = self._lookup_ret_obj(name, model)
        self.name = name
        self.api = api
        self.base_url = api.base_url
        self.token = api.token
        self.url = "{base_url}/{app}/{endpoint}".format(
            base_url=self.base_url,
            app=app.name,
            endpoint=self.name,
        )
        self._choices = None

    def _lookup_ret_obj(self, name, model):
        """Loads unique Response objects.

        This method loads a unique response object for an endpoint if
        it exists. Otherwise return a generic `Record` object.

        :arg str name: Endpoint name.
        :arg obj model: The application model that
            contains unique Record objects.

        :Returns: Record (obj)
        """
        if model:
            name = name.title()
            ret = getattr(model, name, Record)
        else:
            ret = Record
        return ret

    def all(self, limit=None, page=None, sort_by=None):
        """Queries the 'ListView' of a given endpoint.

        Returns all objects from an endpoint.

        :arg int,optional limit: Overrides the max page size on
            paginated returns.  This defines the number of records that will
            be returned with each query to the Netbox server.  The queries
            will be made as you iterate through the result set.
        :arg int,optional offset: Overrides the offset on paginated returns.

        :Returns: A :py:class:`.RecordSet` object.

        :Examples:

        >>> hosts = ctn.monitoring.hosts.all(sort_by={"host.name":"ASC"})
        >>> for host in hosts
        ...   print(host.name)
        ...
        host-1
        host-2
        host-3
        >>>

        If you want to iterate over the results multiple times then
        encapsulate them in a list like this:

        >>> hosts = list(ctn.monitoring.hosts.all())

        This will cause the entire result set to be fetched from the server.

        """
        if sort_by is not None: # Check sort_by format
            if not isinstance(sort_by, dict):
                raise ValueError("sort_by must be a dict. with value as ASC or DSC")
        req = Request(
            base="{}/".format(self.url),
            token=self.token,
            http_session=self.api.http_session,
            limit=limit,
            page=page,
            sort_by=sort_by
        )

        return RecordSet(self, req)

    def get(self, *args, **kwargs):
        r""" Queries the DetailsView of a given endpoint.

        :arg int,optional key: id for the item to be
            retrieved.

        :arg str,optional \**kwargs: Accepts the same keyword args as
            filter(). Any search argument the endpoint accepts can
            be added as a keyword arg.

        :returns: A single :py:class:`.Record` object or None

        :raises ValueError: if kwarg search return more than one value.

        :Examples:        

        Searching for specific hosts

        >>> print(ctn.monitoring.hosts.get(search='{"host.name":"DC1ESX01"}')

        """
        try:
            key = args[0]
        except IndexError:
            key = None

        if not key:
            resp = self.filter(**kwargs)
            ret = next(resp, None)
            if not ret:
                return ret
            try:
                next(resp)
                raise ValueError(
                    "get() returned more than one result. "
                    "Check that the kwarg(s) passed are valid for this "
                    "endpoint or use filter() or all() instead."
                )
            except StopIteration:
                return ret

        req = Request(
            key=key,
            base=self.url,
            token=self.token,
            http_session=self.api.http_session,
        )
        try:
            return next(RecordSet(self, req), None)
        except RequestError as e:
            if e.req.status_code == 404:
                return None
            else:
                raise e

    def filter(self, *args, **kwargs):
        r"""Queries the 'ListView' of a given endpoint.

        Takes named arguments that match the usable filters on a
        given endpoint. If an argument is passed then it's used as a
        freeform search argument if the endpoint supports it.

        :arg str,optional \*args: Freeform search string that's
            accepted on given endpoint.
        :arg str,optional \**kwargs: Any search argument the
            endpoint accepts can be added as a keyword arg.
        :arg int,optional limit: Overrides the max page size on
            paginated returns.  This defines the number of records that will
            be returned with each query to the Netbox server.  The queries
            will be made as you iterate through the result set.
        :arg int,optional offset: Overrides the offset on paginated returns.

        :Returns: A :py:class:`.RecordSet` object.

        :Examples:

        Search host monitoring values with its name

        >>> host = ctn.monitoring.hosts.get(search='{"host.name":"host-2"}')

        Search all hosts monitored with specific pollers
        >>> hosts = list(ctn.monitoring.hosts.filter(search='{"poller.id":"2"}'))

        Search service 

        """

        if args:
            kwargs.update({"q": args[0]})

        if any(i in RESERVED_KWARGS for i in kwargs):
            raise ValueError(
                "A reserved kwarg was passed ({}). Please remove it "
                "and try again.".format(RESERVED_KWARGS)
            )
        limit = kwargs.pop("limit") if "limit" in kwargs else None
        page = kwargs.pop("page") if "page" in kwargs else None
        sort_by = kwargs.pop("sort_by") if "sort_by" in kwargs else None
        if limit is None and page is not None:
            raise ValueError("page requires a positive limit value")
        # BUG : Search with (host_name="DC1ESX01") does not work
        if "search" not in kwargs:
            # Transforms kwargs to Centreon search format
            kwargs_dict = self._create_ctn_search(**kwargs)
        else:
            kwargs_dict = kwargs

        req = Request(
            filters=kwargs_dict,
            base=self.url,
            token=self.token,
            http_session=self.api.http_session,
            limit=limit,
            sort_by=sort_by,
            page=page,
        )

        return RecordSet(self, req)

    def create(self, *args, **kwargs):
        r"""Creates an object on an endpoint.

        Allows for the creation of new objects on an endpoint. Named
        arguments are converted to json properties, and a single object
        is created. Centreon's bulk creation capabilities can be used by
        passing a list of dictionaries as the first argument.

        .. note:

            Any positional arguments will supercede named ones.

        :arg list \*args: A list of dictionaries containing the
            properties of the objects to be created.
        :arg str \**kwargs: key/value strings representing
            properties on a json object.

        :returns: A list or single :py:class:`.Record` object depending
            on whether a bulk creation was requested.

        :Examples:

        Create a new host based on dict

        >>> new_host = {"monitoring_server_id": 2, "name": "test_host", 
                        "address": "127.0.0.1", "alias": "hôte test", 
                        "snmp_community": "RO", 
                        "snmp_version": "2c"}
        >>> ctn = pycentreon.api(centreon_url, token)
        >>> ctn.configuration.hosts.create(new_host)

        """
        req = Request(
            base=self.url,
            token=self.token,
            http_session=self.api.http_session,
        ).post(args[0] if args else kwargs)

        if isinstance(req, list):
            return [self.return_obj(i, self.api, self) for i in req]
        return self.return_obj(req, self.api, self)

    def update(self, objects):
        series = []
        if not isinstance(objects, list):
            raise ValueError(
                "Objects passed must be list[dict|Record] - was {}".format(
                    type(objects)
                )
            )
        for o in objects:
            if isinstance(o, Record):
                data = o.updates()
                if data:
                    data["id"] = o.id
                    series.append(data)
            elif isinstance(o, dict):
                if "id" not in o:
                    raise ValueError("id is missing from object: " + str(o))
                series.append(o)
            else:
                raise ValueError(
                    "Object passed must be dict|Record - was {}".format(type(objects))
                )
        req = Request(
            base=self.url,
            token=self.token,
            http_session=self.api.http_session,
        ).patch(series)

        if isinstance(req, list):
            return [self.return_obj(i, self.api, self) for i in req]
        return self.return_obj(req, self.api, self)

    def delete(self, objects):
        cleaned_ids = []
        if not isinstance(objects, list) and not isinstance(objects, RecordSet):
            raise ValueError(
                "objects must be list[str|int|Record]"
                "|RecordSet - was " + str(type(objects))
            )
        for o in objects:
            if isinstance(o, int):
                cleaned_ids.append(o)
            elif isinstance(o, str) and o.isnumeric():
                cleaned_ids.append(int(o))
            elif isinstance(o, Record):
                if not hasattr(o, "id"):
                    raise ValueError(
                        "Record from '"
                        + o.url
                        + "' does not have an id and cannot be bulk deleted"
                    )
                cleaned_ids.append(o.id)
            else:
                raise ValueError(
                    "Invalid object in list of objects to delete: " + str(type(o))
                )

        req = Request(
            base=self.url,
            token=self.token,
            http_session=self.api.http_session,
        )
        return True if req.delete(data=[{"id": i} for i in cleaned_ids]) else False

    def choices(self):
        if self._choices:
            return self._choices

        req = Request(
            base=self.url,
            token=self.api.token,
            http_session=self.api.http_session,
        ).options()
        try:
            post_data = req["actions"]["POST"]
        except KeyError:
            raise ValueError(
                "Unexpected format in the OPTIONS response at {}".format(self.url)
            )
        self._choices = {}
        for prop in post_data:
            if "choices" in post_data[prop]:
                self._choices[prop] = post_data[prop]["choices"]

        return self._choices

    def count(self, *args, **kwargs):
        if args:
            kwargs.update({"q": args[0]})

        if any(i in RESERVED_KWARGS for i in kwargs):
            raise ValueError(
                "A reserved {} kwarg was passed. Please remove it "
                "try again.".format(RESERVED_KWARGS)
            )

        ret = Request(
            filters=kwargs,
            base=self.url,
            token=self.token,
            http_session=self.api.http_session,
        )

        return ret.get_count()

    def _create_ctn_search(self, **kwargs):
        """Transforms kwargs to Centreon search compatible format

        Returns:
            _type_: _description_
        """
        ordered_kwargs = {}
        ctn_search = {}
        for key in kwargs:
            new_key_name = key.replace("_",".")
            ordered_kwargs[new_key_name] = kwargs[key]
        pass
        ctn_search.update({"search" : f'{ordered_kwargs}'})
        return ctn_search

class DetailEndpoint:
    """Enables read/write operations on detail endpoints.

    Endpoints like ``available-ips`` that are detail routes off
    traditional endpoints are handled with this class.
    """

    def __init__(self, parent_obj, name, custom_return=None):
        self.parent_obj = parent_obj
        self.custom_return = custom_return
        self.url = "{}/{}/{}/".format(parent_obj.endpoint.url, parent_obj.id, name)
        self.request_kwargs = dict(
            base=self.url,
            token=parent_obj.api.token,
            http_session=parent_obj.api.http_session,
        )

    def list(self, **kwargs):
        r"""The view operation for a detail endpoint

        Returns the response from NetBox for a detail endpoint.

        :args \**kwargs: key/value pairs that get converted into url
            parameters when passed to the endpoint.
            E.g. ``.list(method='get_facts')`` would be converted to
            ``.../?method=get_facts``.

        :returns: A :py:class:`.Record` object or list of :py:class:`.Record` objects created
            from data retrieved from NetBox.
        """
        req = Request(**self.request_kwargs).get(add_params=kwargs)

        if self.custom_return:
            return [
                self.custom_return(
                    i, self.parent_obj.endpoint.api, self.parent_obj.endpoint
                )
                for i in req
            ]
        return req

    def create(self, data=None):
        """The write operation for a detail endpoint.

        Creates objects on a detail endpoint in NetBox.

        :arg dict/list,optional data: A dictionary containing the
            key/value pair of the items you're creating on the parent
            object. Defaults to empty dict which will create a single
            item with default values.

        :returns: A :py:class:`.Record` object or list of :py:class:`.Record` objects created
            from data created in NetBox.
        """
        data = data or {}
        req = Request(**self.request_kwargs).post(data)
        if self.custom_return:
            if isinstance(req, list):
                return [
                    self.custom_return(
                        req_item, self.parent_obj.endpoint.api, self.parent_obj.endpoint
                    )
                    for req_item in req
                ]
            else:
                return self.custom_return(
                    req, self.parent_obj.endpoint.api, self.parent_obj.endpoint
                )
        return req


class RODetailEndpoint(DetailEndpoint):
    def create(self, data):
        raise NotImplementedError("Writes are not supported for this endpoint.")
