# ns1ops

CLI script to manage DNS records and monitors using NS1 API

## changelog
- v0.1 released

## requirements
- python 3 (corelib)
- NS1 zone created
- NS1 API key

## limitations
- A record type only
- ping monitor only

## tested
- python 3.7
- unittest for a few methods only

## TODO
- cover code with unittests
- address todos in the code
- something
- ...
- PROFIT!!

## examples
#### help
`ns1ops.py --help`

#### create simple A record
`ns1ops.py record create --zone testzone.cz --name www --ips 8.8.8.8`

#### create RR A record
`ns1ops.py record create --zone testzone.cz --name lb --ips 8.8.4.4,8.8.8.8,1.2.3.4`

#### create A record with monitor
`ns1ops.py record create --zone testzone.cz --name www --ips 8.8.8.8 --monitor`

#### read A record details
`ns1ops.py record read --zone testzone.cz --name www`

#### update A record
`ns1ops.py record update --zone testzone.cz --name www --config '{"meta":{"note": "Created automagically"}}'`

Note: valid JSON string required

#### delete A record
`ns1ops.py record delete --zone testzone.cz --name www`

#### delete A record and cleanup monitor
`ns1ops.py record delete --zone testzone.cz --name www --monitor`

#### create monitor for host www.example.com
`ns1ops.py monitor create --host www.example.com`

#### read all monitors
`ns1ops.py monitor read`

#### read specific monitor
`ns1ops.py monitor read --monitor-id 5e3c495413d96c0128bad89c`

#### update monitor
`ns1ops.py monitor update --monitor-id 5e3c495413d96c0128bad89c --config '{"frequency": 120}'`

#### delete monitor
`python ns1ops.py monitor delete --monitor-id 5e3c495413d96c0128bad89c`




