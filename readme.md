# to-gdas

## What is to-gdas?

to-gdas is a webservice to convert a dataset to GDAS format. Currently the following input formats are supported:

- SDMX
- ODATA
- CSV

## What is GDAS?

GDAS is a schema in XML to be used in a [Table Joining Service](http://www.opengeospatial.org/standards/tjs).

[GDAS Specs](http://geoprocessing.info/tjsdoc/serv?request=HYPERLINKED&schema=GDAS)

## Installation

### Install using Docker

The recommended way to instal to-gdas is using [Docker](http://www.docker.com)

To run to-gdas, use the following commandline:

`docker run -d --restart=always --name to-gdas -p 80:9090 -e "PYTHONUNBUFFERED=0" ojajoh/to-gdas`

Maybe you want to run it behind a corporate proxy, in this case you can pass the proxy settings like this:

`docker run -d --restart=always --name to-gdas -p 80:9090 -e "http_proxy=http://yourproxy:8080" -e "https_proxy=http://yourproxy:8080" -e "no_proxy=your.internal.domain" -e "PYTHONUNBUFFERED=0" ojajoh/to-gdas`

The docker image is automatically build whenever `master` is updated.

### Manual installation

#### Requirements

* [Python 3.x](http://www.python.org/getit/)

Python packages (See also `requirements.txt`):

* [lxml](http://lxml.de/)
* [Requests](http://docs.python-requests.org/en/latest/)
* [Bottle](http://bottlepy.org/docs/dev/index.html)
* [Waitress](https://github.com/Pylons/waitress)

#### Configuration

Edit config.json. The following settings are required:

`host` - The hostname of the machine (default: 0.0.0.0)

`port` - The port to be used (default: 9090)

### Using the service

The service must be called with 3 parameters: `tjs_url`, `framework_uri` and `dataset_url`. Please use a http GET request.

If you are behind a proxy, just set your enviroment variables: `http_proxy`, `https_proxy` and/or `no_proxy`

#### Examples:

for SDMX:

`http://to-gdas.example.com:9090/convert/sdmx?tjs_url=[url]&framework_uri=[uri]&dataset_url=[url]`

for ODATA:

`http://to-gdas.example.com:9090/convert/odata?tjs_url=[url]&framework_uri=[uri]&dataset_url=[url]`

for CSV:

`http://to-gdas.example.com:9090/convert/csv?tjs_url=[url]&framework_uri=[uri]&dataset_url=[url]&dataset_key=[key]`

`tjs_url` should point to the TJS server:

`http://www.mytjshost.com/tjs`

`framework_uri` has to be a `FrameworkURI` that exists on the TJS server:

`http://geodata.nationaalgeoregister.nl/cbsgebiedsindelingen/wfs/CBSGemeente2012`

`dataset_url` should point to an SDMX, ODATA or CSV file, or output of a service, e.g.:

`http://ec.europa.eu/eurostat/SDMX/diss-web/rest/data/hlth_cd_acdr/A..T.TOTAL.G20./?startperiod=2010&endPeriod=2010`

Don't forget to [URL encode](http://www.w3schools.com/tags/ref_urlencode.asp) the request!

The response should be a correct GDAS file wich can be used in a `JoinData` request.
