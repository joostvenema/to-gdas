# to-gdas

## What is to-gdas?

to-gdas is a webservice to convert a dataset to GDAS format. Currently only the SDMX format is supported.

The status is **alpha**. It works, but has no logging or error handling and such.

## What is GDAS?

GDAS is a schema in XML to be used in a [Table Joining Service](http://www.opengeospatial.org/standards/tjs).

[GDAS Specs](http://geoprocessing.info/tjsdoc/serv?request=HYPERLINKED&schema=GDAS)

## Installation

### Requirements

* [Python 3.x](http://www.python.org/getit/)
* [lxml](http://lxml.de/)
* [Requests](http://docs.python-requests.org/en/latest/)
* [Bottle](http://bottlepy.org/docs/dev/index.html) - included
* [Waitress](https://github.com/Pylons/waitress) - included

### Configuration

Edit config.json. The following settings are required:

`host` - The hostname of the machine (default: 127.0.0.1)
`port` - The port to be used (default: 9090)

### Running the app
Start the app: `python3 webapp.py`

To run in the background (linux): `nohup python3 webapp.py > output.log &`

### Using the service

The service must be called with 2 parameters: `framework_url` and `dataset_url`. Please use a http GET request.

example:

`http://to-gdas.example.com:9090/sdmx?framework_url=[url]&dataset_url=[url]`

`framework_url` has to be a `DescribeFrameworks` request to a TJS server:

`http://host/tjs?service=TJS&version=1.0.0&request=DescribeFrameworks&FrameworkURI=[URI]`

`dataset_url` should point to an SDMX file, or output of a service, e.g.:

`http://ec.europa.eu/eurostat/SDMX/diss-web/rest/data/hlth_cd_acdr/A..T.TOTAL.G20./?startperiod=2010&endPeriod=2010`

Don't forget to [URL encode](http://www.w3schools.com/tags/ref_urlencode.asp) the request!

The response should be a correct GDAS file wich can be used in a `JoinData` request. 