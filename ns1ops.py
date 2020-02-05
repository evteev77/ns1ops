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
SUPPORTED_RECORD_TYPES = [A]

class NS1ZoneError(Exception):
    """ Zone level exception """


class NS1RecordError(Exception):
    """ Record level exception """


class NS1MonitorError(Exception):
    """ Monitor level exception """


class NS1NotificationListError(Exception):
    """ Notification list level exception """


class NS1NotificationChannelError(Exception):
    """ Notification channel level exception """


class NS1APIClientError(Exception):
    """ API client level exception """


class NS1APIClient:
    """
    NS1 API client class
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
        Processes request and returns parsed JSON payload
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
    def __init__(self, api_client=NS1APIClient(api_key=NS1_API_KEY)):
        self.api_client = api_client

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

        zone = self._secure_zone(zone)

        if record_type not in SUPPORTED_RECORD_TYPES:
            raise NS1APIClientError('Unsupported record type: {rec_type}'.format(rec_type=record_type))

        endpoint = 'https://api.nsone.net/v1/zones'
        if not all([zone, name, record_type]):
            raise NS1APIClientError('Either "zone", "name" or "record_type" parameter is missed')

        fqdn = '.'.join([name, zone])
        url = '/'.join([endpoint, zone, fqdn, record_type])

        return url

    @staticmethod
    def _secure_ip(address):
        """
        Helper method, validates IP address
        :param dict payload:
        :return: dict
        """

        # TODO: implement address validation
        return address

    @staticmethod
    def _secure_zone(zone):
        """
        Helper method, validates IP address
        :param dict payload:
        :return: dict
        """

        # TODO: implement zone validation
        return zone

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

    def _read_record(self, record_type, zone=None, name=None):
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

    def _update_record(self, record_type, zone=None, name=None, payload=None):
        """
        Updates a record details
        :param str record_type:
        :param str zone:
        :param str name:
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

    def _delete_record(self, record_type, zone=None, name=None):
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


class ARecord(DNSRecord):
    def add_a_record(self, zone, name, ips):
        """
        add A
        """
        return self._create_record(A, zone=zone, name=name, ips=ips)

    def get_a_record(self, zone, name):
        """
        get A
        """
        return self._read_record(A, zone=zone, name=name)

    def update_a_record(self, zone, name, payload):
        """
        upd A
        """
        return self._update_record(A, zone=zone, name=name, payload=payload)

    def delete_a_record(self, zone, name):
        """
        del A
        """
        return self._delete_record(A, zone=zone, name=name)


class NotificationChannel:
    def __init__(self, channel_type, channel_id, channel_value):
        self.type = channel_type
        self.id = channel_id
        self.value = self._secure_id(channel_value)

    @staticmethod
    def _secure_id(id):
        raise NS1NotificationChannelError('You must implement the method in subclass')


class EMailNotification(NotificationChannel):
    @staticmethod
    def _secure_id(email):
        """
        Helper method, validates IP address
        :param dict payload:
        :return: dict
        """

        # TODO: implement email address validation
        return email


class NotificationList:
    def __init__(self, api_client=NS1APIClient(api_key=NS1_API_KEY)):
        self.api_client = api_client

    @staticmethod
    def _get_url(list_id=None):

        endpoint = 'https://api.nsone.net/v1/lists'
        url = endpoint
        if list_id:
            url = '/'.join([endpoint, list_id])

        return url

    def _get_lists(self):
        url = self._get_url()

        return self.api_client.get(url)

    def _get_id_by_name(self, name):
        notification_lists = self._get_lists()

        candidates = [nl.get('id') for nl in notification_lists if nl.get('name') == name]

        if len(candidates) > 1:
            raise NS1NotificationListError('More than one notification lists have name: {}'.format(name))

        if not candidates:
            return

        return candidates[0]

    def _create_list(self, name, channels):
        if not isinstance(channels, list):
            channels = [channels]

        # TODO: pre-check
        list_config = [{'type': channel.type, 'config': {channel.id: channel.value}} for channel in channels]
        payload = {'name': name, 'notify_list': list_config}
        url = self._get_url()

        self.api_client.put(url, payload)

    def _read_list(self, list_id=None, name=None):
        if not any([bool(list_id), bool(name)]):
            raise NS1NotificationListError('Either id or name must be defined')

        if not list_id:
            list_id = self._get_id_by_name(name)
            if not list_id:
                raise NS1NotificationListError('Notification list {} does not exist'.format(name))

        url = self._get_url(list_id=list_id)

        return self.api_client.get(url)

    def _update_list(self, list_id=None, name=None, channels):
        if not any([bool(list_id), bool(name)]):
            raise NS1NotificationListError('Either id or name must be defined')

        if not list_id:
            list_id = self._get_id_by_name(name)
            if not list_id:
                raise NS1NotificationListError('Notification list {} does not exist'.format(name))

        url = self._get_url(list_id=list_id)


    def _delete_list(self):
        pass

