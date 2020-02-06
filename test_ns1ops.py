import ns1ops

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


def test_NS1Monitor_get_url():
    client = ns1ops.Monitor()

    expected = 'https://api.nsone.net/v1/monitoring/jobs'
    assert client._get_url() == expected

    expected = 'https://api.nsone.net/v1/monitoring/jobs/asdfgh123456'
    assert client._get_url(job_id='asdfgh123456') == expected
