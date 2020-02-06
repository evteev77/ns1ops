import ns1ops

import pytest
from mock import Mock, patch


def test_NS1APIClient_set_request():
    client = ns1ops.NS1APIClient(api_key=None)

    # test a call with default values
    request = client._set_request('http://url')
    assert request.full_url == 'http://url'
    assert request.method == 'GET'
    assert request.data is None

    # test a call with all params defined
    request = client._set_request('http://url', method='POST', data={'param': 'value'})
    assert request.method == 'POST'
    assert request.data == b'{"param": "value"}'


@patch('ns1ops.urlopen')
def test_NS1APIClient_get_response(mock_urlopen):
    mock_urlopen.return_value.read.return_value = b'{"content": "something"}'
    client = ns1ops.NS1APIClient(api_key=None)

    # test a normal call
    expected = {'content': 'something'}
    assert client._get_response(None) == expected


def test_NS1APIClient_get_url():
    client = ns1ops.NS1APIClient(api_key=None)

    # test a call with incorrect 'record_type'
    with pytest.raises(ns1ops.NS1APIClientError, match='Unsupported record type: MX'):
        client._get_url(zone='example.com', name='mail', record_type='MX')

    # test a call with 'name' parameter missed
    with pytest.raises(ns1ops.NS1APIClientError, match='Either "zone", "name" or "record_type" parameter is missed'):
        client._get_url(zone='example.com', record_type='A')

    # test a call with 'zone' parameter missed
    with pytest.raises(ns1ops.NS1APIClientError, match='Either "zone", "name" or "record_type" parameter is missed'):
        client._get_url(name='www', record_type='A')

    # test a normal call
    expected = 'https://api.nsone.net/v1/zones/example.com/www.example.com/A'
    assert client._get_url(zone='example.com', name='www', record_type='A') == expected