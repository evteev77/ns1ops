"""
under construction
Author: Sergey Evteev
"""

import os
import json
from urllib.request import urlopen, Request
from urllib.error import HTTPError
import logging

# TODO: move following to arguments
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

NS1_API_KEY = os.environ.get('NS1_API_KEY')
ZONE = 'example.com'

A = 'A'

class NS1ZoneError(Exception):
    """ Zone level exception """


class NS1RecordError(Exception):
    """ Record level exception """


class NS1MonitorError(Exception):
    """ Monitor level exception """


class NS1NotificationListError(Exception):
    """ Notification list level exception """


class NS1APIClientError(Exception):
    """ API client level exception """


class NS1APIClient:
    """
    NS1 API client class, implements CRUD approach to NS1 API
    """

    def __init__(self, api_key):
        self._api_key = api_key

    def _set_request(self, url, method='GET', data=None):
        """
        Helper method, composes urllib.request.Request object
        :param str url:
        :param str method:
        :param dict data:
        :return: urllib.request.Request()
        """

        request = Request(url)
        request.add_header('X-NSONE-Key', self._api_key)
        request.method = method
        if data:
            data = json.dumps(data).encode()
            request.data = data

        return request

    @staticmethod
    def _get_response(request):
        """
        Helper method, processes request and returns parsed JSON payload
        :param urllib.request.Request request:
        :return: dict
        """
        # We expect an exception here to be raised in case of bad request or connection
        response = urlopen(request)

        content = response.read()
        # We assume that content is JSON
        payload = json.loads(content)

        return payload


    @staticmethod
    def _secure_payload(payload):
        """
        Helper method, validates payload
        :param dict payload:
        :return: dict
        """

        # TODO: implement payload validation
        return payload

    def put(self, url, data):
        """
        HTTP PUT interface
        :param str url:
        :param dict data:
        :return: dict
        """

        request = self._set_request(url, method='PUT', data=self._secure_payload(data))

        return self._get_response(request)

    def get(self, url):
        """
        HTTP GET interface
        :param str url:
        :return: dict
        """

        request = self._set_request(url)

        return self._get_response(request)

    def post(self, url, data):
        """
        HTTP POST interface
        :param str url:
        :param dict data:
        :return: dict
        """

        request = self._set_request(url, method='POST', data=self._secure_payload(data))

        return self._get_response(request)

    def delete(self, url):
        """
        HTTP DELETE interface
        :param str url:
        :return: dict
        """

        request = self._set_request(url, method='DELETE')

        return self._get_response(request)


class DNSRecord:
    def __init__(self, api_client=NS1APIClient(api_key=NS1_API_KEY), zone=None, name=None, record_type=None):
        self.api_client = api_client
        self.supported_record_types = ['A']
        self.endpoint = 'https://api.nsone.net/v1/zones'
        self._zone = zone
        self._name = name
        self._record_type = record_type

    @staticmethod
    def _secure_ip(address):
        """
        Helper method, validates IP address
        :param dict payload:
        :return: dict
        """

        # TODO: implement address validation
        return address

    def _get_url(self, zone=None, name=None, record_type=None):
        """
        Helper method, composes valid URL from passed parameters
        :param str zone: 'example.com'
        :param str name: 'www'
        :param str record_type: 'A'
        :return: str
        :raises: NS1APIClientError
        """

        if record_type not in self.supported_record_types:
            raise NS1APIClientError('Unsupported record type: {rec_type}'.format(rec_type=record_type))


        if not all([zone, name, record_type]):
            raise NS1APIClientError('Either "zone", "name" or "record_type" parameter is missed')

        fqdn = '.'.join([name, zone])
        url = '/'.join([self.endpoint, zone, fqdn, record_type])

        return url

    def _create(self, record_type, zone=None, name=None, ips=None):
        """
        Creates a record in specified zone
        :param str record_type:
        :param str zone:
        :param str name:
        :param list ips:
        :return: dict
        :raises: NS1RecordError
        """

        if not ips:
            raise NS1RecordError('Parameter "ips" is missed')

        url = self._get_url(zone=zone, name=name, record_type=record_type)
        try:
            self.api_client.get(url)
        except HTTPError as e:
            if e.code == 404:
                # record not found, continue processing
                pass
            else:
                raise
        else:
            raise NS1RecordError('{type} record for {name} at {zone} already exists.'.format(type=type, name=name, zone=zone))

        if not isinstance(ips, list):
            ips = [ips]

        ips = [self._secure_ip(address) for address in ips]
        payload = {
            'zone': zone,
            'domain': '.'.join([name, zone]),
            'type': record_type,
            'answers': [{'answer': [ip]} for ip in ips]
        }

        return self.api_client.put(url, payload)

    def _read(self, record_type, zone=None, name=None):
        """
        Reads a record details
        :param str record_type:
        :param str zone:
        :param str name:
        :return: dict
        """

        url = self._get_url(zone=zone, name=name, record_type=record_type)
        try:
            return self.api_client.get(url)
        except HTTPError as e:
            if e.code == 404:
                return

            raise

    def _update(self, record_type, zone=None, name=None, payload=None):
        """
        Updates a record details
        :param str record_type:
        :param str zone:
        :param str name:
        :param dict payload:
        :return: dict
        """

        url = self._get_url(zone=zone, name=name, record_type=record_type)
        try:
            self.api_client.get(url)
        except HTTPError as e:
            if e.code == 404:
                raise NS1RecordError('{type} record for {name} at {zone} does not exists.'.format(type=type, name=name, zone=zone))
            else:
                raise

        if not payload:
            raise NS1RecordError('Parameter "payload" is missed')

        return self.api_client.post(url, payload)

    def _delete(self, record_type, zone=None, name=None):
        """
        Deletes a record
        :param str record_type:
        :param str zone:
        :return: dict # empty
        """

        url = self._get_url(zone=zone, name=name, record_type=record_type)

        try:
            self.api_client.delete(url)
        except HTTPError as e:
            if e.code == 404:
                return

            raise

    def __repr__(self):
        return


class ARecord(DNSRecord):
    def __init__(self, zone=None, name=None):
        super().__init__(zone=zone, name=name, record_type='A')

    def add(self, ips=None):
        """
        add A
        """

        return self._create(A, zone=self._zone, name=self._name, ips=ips)

    def get(self):
        """
        get A
        """

        return self._read(A, zone=self._zone, name=self._name)

    def update(self, payload=None):
        """
        upd A
        """

        return self._update(A, zone=self._zone, name=self._name, payload=payload)

    def delete(self):
        """
        del A
        """

        return self._delete(A, zone=self._zone, name=self._name)


class Monitor:
    def __init__(self, api_client=NS1APIClient(api_key=NS1_API_KEY)):
        self.api_client = api_client
        self.endpoint = 'https://api.nsone.net/v1/monitoring/jobs'

    def _get_url(self, job_id=None):
        """
        Helper method, composes valid URL from passed parameters
        :param str job_id:
        :return: str
        :raises: NS1APIClientError
        """

        url = self.endpoint
        if job_id:
            url = '/'.join([self.endpoint, job_id])

        return url

    