# !/usr/bin/env python3
#
# to-gdas - A * to GDAS conversion service
#

from bottle import Bottle, run, request, response
from lxml import etree
import json
import requests
import messytables as mt
import io

with open('config.json', 'r') as f:
    cfg = json.load(f)

app = Bottle()


# Just like str(), but return an empty string instead of None
def xstr(s):
    if s is None:
        return ''
    else:
        return str(s)


#
# Fetch framework from remote server and return as XML element
#
def get_framework(tjs_url, framework_uri):
    # Fetch and proces TJS framework
    try:
        payload = {'service': 'TJS',
                   'version': '1.0.0',
                   'request': 'DescribeFrameworks',
                   'FrameworkURI': framework_uri}
        y = requests.get(tjs_url, params=payload, verify=False)
        xml = etree.fromstring(y.content)
        xml_temp = etree.tostring(xml[0])
        # Quick&dirty removal of namespace prefix
        root = xml_temp.replace(b'ns0:', b'')
        parser = etree.XMLParser(ns_clean=True, encoding='utf-8')
        framework = etree.fromstring(root, parser=parser)

        return framework

    except Exception as err:
        print(err)


def get_csv(csv_url, csv_key):
    # Fetch and proces CSV dataset
    y = requests.get(csv_url, verify=False)
    f = io.BytesIO(y.content)

    table_set = mt.CSVTableSet(f)
    row_set = table_set.tables[0]
    offset, headers = mt.headers_guess(row_set.sample)
    row_set.register_processor(mt.headers_processor(headers))
    row_set.register_processor(mt.offset_processor(offset + 1))
    types = mt.type_guess(row_set.sample, strict=True)
    row_set.register_processor(mt.types_processor(types))

    dataset = etree.Element("Dataset")
    etree.SubElement(dataset, "DatasetURI").text = 'N_A'
    etree.SubElement(dataset, "Organization").text = 'N_A'
    etree.SubElement(dataset, "Title").text = 'N_A'
    etree.SubElement(dataset, "Abstract").text = 'N_A'
    etree.SubElement(dataset, "ReferenceDate").text = 'N_A'
    etree.SubElement(dataset, "Version").text = '0'
    etree.SubElement(dataset, "Documentation").text = 'N_A'
    columnset = etree.SubElement(dataset, "Columnset")
    fkey = etree.SubElement(
        columnset,
        "FrameworkKey",
        complete="true",
        relationship="one")
    attrib = etree.SubElement(columnset, "Attributes")

    for header in (row_set.sample.__next__()):
        header_type = type(header.type).__name__.lower()[:-4]
        if header.column == csv_key:
            col = etree.SubElement(
                fkey,
                "Column",
                name=header.column,
                type="http://www.w3.org/TR/xmlschema-2/#" + header_type,
                length="")
        else:
            col = etree.SubElement(
                attrib,
                "Column",
                name=header.column,
                type="http://www.w3.org/TR/xmlschema-2/#" + header_type,
                length="")
            etree.SubElement(col, "Title").text = "N_A"
            etree.SubElement(col, "Abstract").text = "N_A"
    rowset = etree.SubElement(dataset, "Rowset")

    # For some reason the offset doesn't work, so we skip the headers with
    # a workaround
    iter_rows = iter(row_set)
    next(iter_rows)
    for row in iter_rows:
        rw = etree.SubElement(rowset, "Row")
        for cell in row:
            if cell.column == csv_key:
                k = etree.SubElement(rw, "K")
            else:
                k = etree.SubElement(rw, "V")
            k.text = str(cell.value)

    return dataset


def get_sdmx(sdmx_url):
    # Fetch and process SDMX dataset
    try:
        y = requests.get(sdmx_url, verify=False)
        xml = etree.fromstring(y.content)
        xslt_root = etree.parse("xslt/sdmx-gdas.xsl")
        transform = etree.XSLT(xslt_root)
        dataset = etree.fromstring(str((transform(xml))))

        return dataset

    except Exception as err:
        print(err)


def get_odata(odata_url):
    # Fetch and process ODATA dataset
    y = requests.get(odata_url, verify=False)
    data = y.json()
    # Get root_url
    root_url = data['odata.metadata'].split('$')[0]
    # Get TableInfos
    dataset = etree.Element("Dataset")
    y = requests.get(root_url + 'TableInfos', verify=False)
    tbl = y.json()['value'][0]
    etree.SubElement(dataset, "DatasetURI").text = tbl['Identifier']
    etree.SubElement(dataset, "Organization").text = tbl['Catalog']
    etree.SubElement(dataset, "Title").text = tbl['Title']
    etree.SubElement(dataset, "Abstract").text = tbl['Summary']
    etree.SubElement(dataset, "ReferenceDate").text = tbl['Period']
    etree.SubElement(dataset, "Version").text = '0'
    etree.SubElement(dataset, "Documentation").text = 'N_A'

    # Get DataProperties
    y = requests.get(root_url + 'DataProperties', verify=False)
    data_properties = y.json()
    columnset = etree.SubElement(dataset, "Columnset")
    fkey = etree.SubElement(
        columnset,
        "FrameworkKey",
        complete="true",
        relationship="one")
    attrib = etree.SubElement(columnset, "Attributes")
    col_pos = []
    for column in data_properties['value']:
        if column['Type'] == 'GeoDimension':
            col = etree.SubElement(
                fkey,
                "Column",
                name=column['Key'],
                type="http://www.w3.org/TR/xmlschema-2/#string",
                length="")
            col_pos.append([column['Position'], column['Key'], 'K'])
        else:
            col = etree.SubElement(
                attrib,
                "Column",
                name=column['Key'],
                type="http://www.w3.org/TR/xmlschema-2/#string",
                length="")
            etree.SubElement(col, "Title").text = column['Title']
            etree.SubElement(col, "Abstract").text = column['Description']
            col_pos.append([column['Position'], column['Key'], 'V'])
    rowset = etree.SubElement(dataset, "Rowset")
    rows = data['value']
    for row in rows:
        rw = etree.SubElement(rowset, "Row")
        for col in col_pos:
            k = etree.SubElement(rw, col[2])
            k.text = xstr(row[col[1]])

    return dataset


@app.route('/', method='GET')
def index():
    return '''Convert ODATA, SDMX and CSV to GDAS.<br><br>
        https://github.com/joostvenema/to-gdas'''


@app.route('/convert/<filetype>', method='GET')
def convert(filetype):
    # get query parameters
    tjs_url = request.params.tjs_url
    framework_uri = request.params.framework_uri
    dataset_url = request.params.dataset_url
    dataset_key = request.params.dataset_key

    # print some info
    print('tjs_url: ' + tjs_url)
    print('framework_uri: ' + framework_uri)
    print('dataset_url: ' + dataset_url)
    print('dataset_key: ' + dataset_key)

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
    if filetype == 'sdmx':
        dataset = get_sdmx(dataset_url)
    elif filetype == 'odata':
        dataset = get_odata(dataset_url)
    elif filetype == 'csv':
        dataset = get_csv(dataset_url, dataset_key)
    else:
        response.status = 500
        return 'No valid endpoint. Must be: sdmx, odata or csv'

    root[0].append(dataset)

    response.content_type = 'application/xml'
    return etree.tostring(root, pretty_print=True)

run(app, host=cfg['host'], port=cfg['port'], reloader=True, server='waitress')
