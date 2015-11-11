# !/usr/bin/env python3
#
# to-gdas - A * to GDAS conversion service
#
# Currently only the SDMX format is supported,
# with the GEO attribute as framework-key
#
# version 0.6

from bottle import Bottle, run, request, response
from lxml import etree
import json
import requests

with open('config.json', 'r') as f:
    cfg = json.load(f)

app = Bottle()


def get_framework(tjs_url, framework_uri):
    # Fetch and proces TJS framework
    try:
        payload = {'service': 'TJS',
                   'version': '1.0.0',
                   'request': 'DescribeFrameworks',
                   'FrameworkURI': framework_uri}
        y = requests.get(tjs_url, params=payload)
        xml = etree.fromstring(y.content)
        xml_temp = etree.tostring(xml[0])
        # Quick&dirty removal of namespace prefix
        root = xml_temp.replace(b'ns0:', b'')
        parser = etree.XMLParser(ns_clean=True, encoding='utf-8')
        framework = etree.fromstring(root, parser=parser)

        return framework

    except Exception as err:
        print(err)


def get_sdmx(sdmx_url):
    # Fetch and process SDMX dataset
    try:
        y = requests.get(sdmx_url)
        xml = etree.fromstring(y.content)
        xslt_root = etree.parse("xslt/sdmx-gdas.xsl")
        transform = etree.XSLT(xslt_root)
        dataset = etree.fromstring(str((transform(xml))))

        return dataset

    except Exception as err:
        print(err)


def get_odata(odata_url):
    # Fetch and process ODATA dataset
    # gdas = {}
    try:
        y = requests.get(odata_url)
        data = y.json()
        # Get root_url
        root_url = data['odata.metadata'].split('$')[0]
        # Get TableInfos
        dataset = etree.Element("Dataset")
        y = requests.get(root_url + 'TableInfos')
        tbl = y.json().value[0]
        etree.SubElement(dataset, "DatasetURI").text = tbl['Identifier']
        etree.SubElement(dataset, "Organization").text = tbl['Catalog']
        etree.SubElement(dataset, "Title").text = tbl['Title']
        etree.SubElement(dataset, "Abstract").text = tbl['Summary']
        etree.SubElement(dataset, "ReferenceDate").text = tbl['Period']
        etree.SubElement(dataset, "Version").text = '0'
        etree.SubElement(dataset, "Documentation").text = 'N_A'

        # Get DataProperties
        y = requests.get(root_url + 'DataProperties')
        data_properties = y.json()
        columnset = etree.SubElement(dataset, "Columnset")
        fkey = etree.SubElement(
            columnset,
            "FrameworkKey",
            complete="true",
            relationship="one")
        attrib = etree.SubElement(columnset, "Attributes")

        for column in data_properties['value']:
            if column['Type'] == 'GeoDimension':
                col = etree.SubElement(
                    fkey,
                    "Column",
                    name=column['Key'],
                    type="http://www.w3.org/TR/xmlschema-2/#string",
                    length="")
                key_position = column['Position']
            else:
                col = etree.SubElement(
                    attrib,
                    "Column",
                    name=column['Key'],
                    type="http://www.w3.org/TR/xmlschema-2/#string",
                    length="")
                etree.SubElement(col, "Title").text = column['Title']
                etree.SubElement(col, "Abstract").text = column['Description']
        rowset = etree.SubElement(dataset, "Rowset")

        for row in data.value:
            rw = etree.SubElement(rowset, "Row")
            for idx, value in enumerate(row):
                if idx == key_position:
                    k = etree.SubElement(rw, "K")
                    k.text = value
                else:
                    v = etree.SubElement(rw, "V")
                    v.text = value

        return dataset

    except Exception as err:
        print(err)


@app.route('/', method='GET')
def index():
    return '''Convert ODATA, SDMX to GDAS.
        https://github.com/joostvenema/to-gdas'''


@app.route('/sdmx', method='GET')
def convert():
    # get query parameters
    tjs_url = request.params.tjs_url
    framework_uri = request.params.framework_uri
    dataset_url = request.params.dataset_url
    # Setup XML elements
    root = etree.Element(
        "GDAS",
        version="1.0",
        service="TJS",
        capabilities="http://sis.agr.gc.ca/pls/meta/tjs_1x0_getcapabilities",
        xmlns="http://www.opengis.net/tjs/1.0")

    # Get TJS framework
    framework = get_framework(tjs_url, framework_uri)
    # Append TJS framework
    root.append(framework)
    # Append dataset
    dataset = get_sdmx(dataset_url)
    root[0].append(dataset)

    response.content_type = 'application/xml'

    return etree.tostring(root, pretty_print=True)

run(app, host=cfg['host'], port=cfg['port'], reloader=True, server='waitress')
