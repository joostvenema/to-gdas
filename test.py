# -*- coding: utf-8 -*-
"""test.py

Simple, straight forwarded test script for to-gdas.

Assumes to-gdas is running on port 9090, and the contents of the /test folder
are being served over port 8000 as sample/mock files. To setup a quick
http server with Python, go into the testfolder and run: python -m http.server

"""

import requests

to_gdas_server = 'http://localhost:9090'
mock_server = 'http://localhost:8000'
framework_uri = 'http://geodata.nationaalgeoregister.nl/cbsgebiedsindelingen/wfs/CBSGemeente2012'

payload = {'tjs_url': mock_server + '/mock-describe-frameworks-response.xml',
           'framework_uri': framework_uri}

# Check if webservers are available

y = requests.get(to_gdas_server)
if (y.status_code != 200):
    print('Error connecting to to-gdas server!')

y = requests.get(mock_server)
if (y.status_code != 200):
    print('Error connecting to mockserver!')

# sdmx
print('Test SDMX')
payload['dataset_url'] = mock_server + '/sample-sdmx.xml'
y = requests.get(to_gdas_server + '/convert/sdmx', params=payload)

if (y.status_code == 200):
    print('Succes!')
else:
    print('Fail! HTTP status code ' + y.status_code)

# odata
print('Test ODATA')
payload['dataset_url'] = mock_server + '/sample-odata.json'
y = requests.get(to_gdas_server + '/convert/odata', params=payload)

if (y.status_code == 200):
    print('Succes!')
else:
    print('Fail! HTTP status code ' + y.status_code)

# csv
print('Test CSV')
payload['dataset_url'] = mock_server + '/sample-csv.csv'
payload['dataset_key'] = 'CBS_code'
y = requests.get(to_gdas_server + '/convert/csv', params=payload)

if (y.status_code == 200):
    print('Succes!')
else:
    print('Fail! HTTP status code ' + str(y.status_code))
