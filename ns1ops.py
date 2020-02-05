"""
under construction
Author: Sergey Evteev
"""

import os
import json
from urllib.request import urlopen, Request
import logging

# TODO: move following to arguments
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

NS1_API_KEY = os.environ.get('NS1_API_KEY')
ZONE = 'example.com'

A = 'A'
SUPPORTED_RECORD_TYPES = [A]

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
        request.data = data

        return request

    @staticmethod
    def _get_response(request):
        """
        Helper method, processes request and returns parsed JSON payload
        :param urllib.request.Request request:
        :return: dict
        """

        logger.debug('{method}: {url}'.format(method=request.method, url=request.full_url))
        # We expect an exception here to be raised in case of bad request or connection
        response = urlopen(request)

        content = response.read()
        # We assume that content is JSON
        payload = json.loads(content)

        return payload

    @staticmethod
    def _get_url(zone=None, name=None, record_type=None):
        """
        Helper method, composes valid URL from passed parameters
        :param str zone: 'example.com'
        :param str name: 'www'
        :param str record_type: 'A'
        :return: str
        :raises: NS1APIClientError
        """

        if record_type not in SUPPORTED_RECORD_TYPES:
            raise NS1APIClientError('Unsupported record type: {rec_type}'.format(rec_type=record_type))

        endpoint = 'https://api.nsone.net/v1/zones'
        if not all([zone, name, record_type]):
            raise NS1APIClientError('Either "zone", "name" or "record_type" parameter is missed')

        fqdn = '.'.join([zone, name])
        url = '/'.join([endpoint, zone, fqdn, record_type])

        return url

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
    def __init__(self, api_client=NS1APIClient(api_key=NS1_API_KEY)):
        self.api_client = api_client

    @staticmethod
    def _secure_ip(address):
        """
        Helper method, validates IP address
        :param dict payload:
        :return: dict
        """

        # TODO: implement address validation
        return address

    def _create_record(self, record_type, zone=None, name=None, ips=None):
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

        try:
            self._read_record(record_type, zone=zone, name=name)
        except HTTPError as e:
            if e.code == 404:
                # record not found, continue processing
                pass
            else:
                raise
        else:
            raise NS1RecordError('{type} record for {name} at {zone} already exists.'.format(type=type, name=name, zone=zone))

        url = self.api_client._get_url(zone=zone, name=name, record_type=record_type)

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

    def _read_record(self, record_type, zone=None, name=None):
        """
        Reads a record details
        :param str record_type:
        :param str zone:
        :param str name:
        :return: dict
        """

        try:
            self._read_record(record_type, zone=zone, name=name)
        except HTTPError as e:
            if e.code == 404:
                return

            raise

        url = self.api_client._get_url(zone=zone, name=name, record_type=record_type)

        return self.api_client.get(url)

    def _update_record(self, record_type, zone=None, name=None, payload=None):
        """
        Updates a record details
        :param str record_type:
        :param str zone:
        :param str name:
        :return: dict
        """

        try:
            self._read_record(record_type, zone=zone, name=name)
        except HTTPError as e:
            if e.code == 404:
                raise NS1RecordError('{type} record for {name} at {zone} does not exists.'.format(type=type, name=name, zone=zone))
            else:
                raise

        url = self.api_client._get_url(zone=zone, name=name, record_type=record_type)
        if not payload:
            raise NS1RecordError('Parameter "payload" is missed')

        return self.api_client.post(url, payload)

    def _delete_record(self, record_type, zone=None, name=None):
        """
        Deletes a record
        :param str record_type:
        :param str zone:
        :return: dict # empty
        """

        url = self.api_client._get_url(zone=zone, name=name, record_type=record_type)

        try:
            self.api_client.delete(url)
        except HTTPError as e:
            if e.code == 404:
                return

            raise

    def add_a_record(self, zone, name, ips):

        return self._create_record(A, zone=zone, name=name, ips=ips)

    def get_a_record(self, zone, name):

        return self._read_record(A, zone=zone, name=name)

    def update_a_record(self, zone, name, payload):

        return self._update_record(A, zone=zone, name=name, payload=payload)

    def delete_a_record(self, zone, name):

        return self._delete_record(A, zone=zone, name=name)


