# to-gdas

## What is to-gdas?

to-gdas is a webservice to convert a dataset to GDAS format. Currently the following input formats are supported:

- SDMX
- ODATA
- CSV

The status is **alpha**. It works, but has no logging or error handling and such.

## What is GDAS?

GDAS is a schema in XML to be used in a [Table Joining Service](http://www.opengeospatial.org/standards/tjs).

[GDAS Specs](http://geoprocessing.info/tjsdoc/serv?request=HYPERLINKED&schema=GDAS)

## Installation

### Install using Docker

[Docker](http://docker.io) "is an open platform for developers and sysadmins to build, ship, and run distributed applications."

To run to-gdas, use the following commandline: `docker run -d ojajoh/to-gdas to-gdas`

The docker image is automatically build whenever `master` is updated.

### Manual installation

#### Requirements

* [Python 3.x](http://www.python.org/getit/)
* [lxml](http://lxml.de/)
* [Requests](http://docs.python-requests.org/en/latest/)
* [Bottle](http://bottlepy.org/docs/dev/index.html)
* [Waitress](https://github.com/Pylons/waitress)

#### Configuration

Edit config.json. The following settings are required:

`host` - The hostname of the machine (default: 0.0.0.0)

`port` - The port to be used (default: 9090)

#### Running the app
Start the app: `python3 webapp.py`

To run in the background (linux): `nohup python3 webapp.py > output.log &`

### Using the service

The service must be called with 3 parameters: `tjs_url`, `framework_uri` and `dataset_url`. Please use a http GET request.

If you are behind a proxy, just set your enviroment variables: `http_proxy`, `https_proxy` and/or `no_proxy`



#### example:

for SDMX:

`http://to-gdas.example.com:9090/sdmx?tjs_url=[url]&framework_uri=[uri]&dataset_url=[url]`

for ODATA:

`http://to-gdas.example.com:9090/odata?tjs_url=[url]&framework_uri=[uri]&dataset_url=[url]`

for CSV:

`http://to-gdas.example.com:9090/csv?tjs_url=[url]&framework_uri=[uri]&dataset_url=[url]&dataset_key=[key]`

`tjs_url` should point to the TJS server:

`http://www.mytjshost.com/tjs`

`framework_uri` has to be a `FrameworkURI` that exists on the TJS server:

`http://geodata.nationaalgeoregister.nl/cbsgebiedsindelingen/wfs/CBSGemeente2012`

`dataset_url` should point to an SDMX, ODATA or CSV file, or output of a service, e.g.:

`http://ec.europa.eu/eurostat/SDMX/diss-web/rest/data/hlth_cd_acdr/A..T.TOTAL.G20./?startperiod=2010&endPeriod=2010`

Don't forget to [URL encode](http://www.w3schools.com/tags/ref_urlencode.asp) the request!

The response should be a correct GDAS file wich can be used in a `JoinData` request.
