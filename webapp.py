# !/usr/bin/env python3
# 
# to-gdas - A * to GDAS conversion service
#
# Currently only the SDMX format is supported, with the GEO attribute as framework-key
#
# version 0.1

from bottle import Bottle, run, route, request, response
from lxml import etree
import json
import requests

with open('config.json', 'r') as f:
    cfg = json.load(f)

app = Bottle()

def get_framework(framework_url):
    # Fetch and proces TJS framework
    try:
        y = requests.get(framework_url)    
        xml = etree.fromstring(y.content)
        xml_temp = etree.tostring(xml[0])
        # Quick&dirty removal of namespace prefix
        root  = xml_temp.replace(b'ns0:', b'')
        parser = etree.XMLParser(ns_clean=True, encoding='utf-8')
        framework = etree.fromstring(root, parser=parser)

        return framework

    except Exception as err:
        print(err)
        return None

def get_sdmx(sdmx_url):
    # Fetch and proces SDMX dataset
    try:
        y = requests.get(sdmx_url)     
        xml = etree.fromstring(y.content)
        xslt_root = etree.parse("xslt/sdmx-gdas.xsl")
        transform = etree.XSLT(xslt_root)
        dataset = etree.fromstring(str((transform(xml))))

        return dataset

    except Exception as err:
        print(err)
        return None

@app.route('/', method='GET')
def index():
    return 'This webservice converts SDMX to GDAS'

@app.route('/sdmx', method='GET')
def convert():
    # get query parameters
    framework_url = request.query.framework_url
    dataset_url = request.query.dataset_url
    # Setup XML elements
    root = etree.Element("GDAS", version="1.0", service="TJS", 
        capabilities="http://sis.agr.gc.ca/pls/meta/tjs_1x0_getcapabilities",
        xmlns="http://www.opengis.net/tjs/1.0")
    # Append TJS framework
    root.append(get_framework(framework_url))
    # Append dataset
    dataset = get_sdmx(dataset_url)
    root[0].append(dataset)

    response.content_type = 'application/xml'

    return etree.tostring(root, pretty_print=True)

run(app, host=cfg['host'], port=cfg['port'], reloader=True, server='waitress')