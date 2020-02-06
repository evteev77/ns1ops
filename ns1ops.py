"""
under construction
Author: Sergey Evteev
"""

import argparse
import os
import json
from urllib.request import urlopen, Request
from urllib.error import HTTPError
import logging

# TODO: move following to arguments
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

NS1_API_KEY = None

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
    def __init__(self, api_client=None, zone=None, name=None, record_type=None):
        """
        DNS Record class
        :param NSAPIClient api_client:
        :param str zone: example.com
        :param str name: www
        :param str record_type: A
        :raises: NS1APIClientError
        """

        if not all([zone, name, record_type]):
            raise NS1APIClientError('Either "zone", "name" or "record_type" parameter is missed')

        self._api_client = api_client

        self.supported_record_types = ['A']
        if record_type not in self.supported_record_types:
            raise NS1APIClientError('Unsupported record type: "{rec_type}"'.format(rec_type=record_type))

        self._endpoint = 'https://api.nsone.net/v1/zones'
        self._zone = zone
        self._name = name
        self._record_type = record_type

        self._fqdn = '.'.join([name, zone])
        self._url = '/'.join([self._endpoint, zone, self._fqdn, record_type])

    @staticmethod
    def _secure_ip(address):
        """
        Helper method, validates IP address
        :param str address:
        :return: str
        """

        # TODO: implement address validation
        return address

    @staticmethod
    def _secure_payload(payload):
        """
        Helper method, validates IP address
        :param dict payload:
        :return: dict
        """

        if not payload:
            raise NS1RecordError('Configuration to update is missed')

        if not isinstance(payload, dict):
            raise NS1RecordError('Configuration to update has incorrect format')

        return payload

    def create(self, ips=None, monitor=None):
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
            self._api_client.get(self._url)
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
            'zone': self._zone,
            'domain': self._fqdn,
            'type': self._record_type,
            'answers': [{'answer': [ip]} for ip in ips]
        }


        result = {'record': self._api_client.put(self._url, payload)}

        if monitor:
            job = monitor(api_client=self._api_client, host=self._fqdn)
            result['monitor'] = job.create()

        return result

    def read(self):
        """
        Reads a record details
        :return: dict
        :raises: HTTPError
        """

        try:
            return self._api_client.get(self._url)
        except HTTPError as e:
            if e.code == 404:
                return

            raise

    def update(self, payload):
        """
        Updates a record details
        :param dict payload:
        :return: dict
        :raises: HTTPError
        :raises: NS1RecordError
        """

        try:
            self._api_client.get(self._url)
        except HTTPError as e:
            if e.code == 404:
                raise NS1RecordError('{type} record for {name} at {zone} does not exists.'.format(type=self._record_type, name=self._name, zone=self._zone))
            else:
                raise

        return self._api_client.post(self._url, self._secure_payload(payload))

    def delete(self):
        """
        Deletes a record
        :param str record_type:
        :param str zone:
        :return: dict # empty
        :raises: HTTPError
        """

        try:
            self._api_client.delete(self._url)
        except HTTPError as e:
            if e.code == 404:
                return

            raise

    def __repr__(self):
        return '<DNSRecord type {rec_type} for {name} at {zone}'.format(rec_type=self._record_type, name=self._name, zone=self._zone)


class ARecord(DNSRecord):
    def __init__(self, api_client=None, zone=None, name=None):
        super().__init__(api_client=api_client, zone=zone, name=name, record_type='A')

class MXRecord(DNSRecord):
    def __init__(self, *args, **kwargs):
        raise NS1RecordError('MX record is not implemented yet')

class NSRecord(DNSRecord):
    def __init__(self, *args, **kwargs):
        raise NS1RecordError('NS record is not implemented yet')


class Monitor:
    def __init__(self, api_client=None, monitor_type=None, host=None, region='sjc', frequency=60, monitor_id=None):
        self._api_client = api_client
        self._endpoint = 'https://api.nsone.net/v1/monitoring/jobs'
        self._id = monitor_id
        self._host = host
        self._monitor_type = monitor_type
        self._frequency = frequency
        self._regions = [region]

    @staticmethod
    def _secure_payload(payload):
        """
        Helper method, validates IP address
        :param dict payload:
        :return: dict
        """

        if not payload:
            raise NS1MonitorError('Configuration to update is missed')

        if not isinstance(payload, dict):
            raise NS1MonitorError('Configuration to update has incorrect format')

        return payload

    def _get_url(self, job_id=None):
        """
        Helper method, composes valid URL from passed parameters
        :param str job_id:
        :return: str
        """

        url = self._endpoint
        if job_id:
            url = '/'.join([self._endpoint, job_id])

        return url

    def activate(self):
        self.update(payload={'active': True})

    def deactivate(self):
        self.update(payload={'active': False})

    def create(self):
        payload = {
            'name': '{name} {mon_type} check'.format(name=self._host, mon_type=self._monitor_type),
            'job_type': self._monitor_type,
            'region_scope': 'fixed',
            'regions': self._regions,
            'frequency': self._frequency,
            'config': {'host': self._host}}

        url = self._get_url()
        result = self._api_client.put(url, payload)

        self._id = result.get('id')

        return result

    def read(self):
        url = self._get_url()
        if self._id:
            url = self._get_url(job_id=self._id)

        return self._api_client.get(url)

    def update(self, payload):
        url = self._get_url(job_id=self._id)

        return self._api_client.post(url, self._secure_payload(payload))

    def delete(self):
        url = self._get_url(job_id=self._id)

        return self._api_client.delete(url)

    def __repr__(self):
        return '<Monitor {mon_type} for {host} ({mon_id})>'.format(mon_type=self._monitor_type, host=self._host, mon_id=self._id)


class PingMonitor(Monitor):
    def __init__(self, api_client=None, host=None, monitor_id=None):
        super().__init__(api_client=api_client, monitor_type='ping', host=host, monitor_id=monitor_id)

class TCPMonitor(Monitor):
    def __init__(self, *args, **kwargs):
        raise NS1MonitorError('TCP monitor is not implemented yet')


def get_arguments():
    parser = argparse.ArgumentParser(description='NS1 operations tool')
    parser.add_argument('resource', type=str, help='Resource to operate', choices=['record', 'monitor'])
    parser.add_argument('operation', type=str, help='CRUD operation', choices=['create', 'read', 'update', 'delete'])
    parser.add_argument('--resource-type', type=str, help='Resource type in context of resource', default='default')
    parser.add_argument('--zone', type=str, help='DNS zone for a record')
    parser.add_argument('--name', type=str, help='Hostname (w/o domain)')
    parser.add_argument('--ips', type=str, help='List of IP addresses, comma-separated')
    parser.add_argument('--monitor', help='Add default monitor when creating record', action='store_true')
    parser.add_argument('--monitor-id', type=str, help='ID of existing monitor')
    parser.add_argument('--config', type=dict, help='Configuration to update')
    parser.add_argument('--api-key', type=str, help='NS1 API key')

    return parser.parse_args()


def get_api_client(args):
    api_key = args.api_key or os.environ.get('NS1_API_KEY')
    if not api_key:
        raise NS1APIClientError('Either provide NS1 API key as a parameter or define NS1_API_KEY env variable')

    return NS1APIClient(api_key=api_key)


def method_selector(instance):
    method_map = {
        'create': instance.create,
        'read': instance.read,
        'update': instance.update,
        'delete': instance.delete,
    }

    return method_map


def class_selector(resource):
    resource_map = {
        'record': {
            'A': ARecord,
            'MX': MXRecord,
            'NS': NSRecord,
            'default': ARecord,
        },
        'monitor': {
            'ping': PingMonitor,
            'tcp': TCPMonitor,
            'default': PingMonitor,
        }
    }

    return resource_map[resource]


def main():
    args = get_arguments()

    res_args = {'api_client': get_api_client(args)}
    ops_args = {}

    if args.resource == 'record':
        res_args['zone'] = args.zone
        res_args['name'] = args.name
        if args.operation == 'create':
            ops_args['ips'] = args.ips.split(',')
            if args.monitor:
                ops_args['monitor'] = class_selector('monitor')['default']

    elif args.resource == 'monitor':
        res_args['host'] = args.name
        res_args['monitor_id'] = args.monitor_id

    if args.operation == 'update':
        ops_args['payload'] = args.config

    resource = class_selector(args.resource)[args.resource_type](**res_args)
    result = method_selector(resource)[args.operation](**ops_args)

    print(result)


if __name__ == '__main__':
    main()
