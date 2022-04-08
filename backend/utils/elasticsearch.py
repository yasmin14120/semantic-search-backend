#
# encoding: utf-8
#
# This module provides utility functions for Elasticsearch.
#
# devs@droxit.de
#
# Copyright (c) 2019 droxIT GmbH
#

import json
import os
import glob
import logging
import requests
from requests import Response


TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), './templates/')
HEADERS = {"content-type": "application/json"}
ES_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

logger = logging.getLogger(__name__)


def es_request(method: str, url: str, data=None) -> Response:
    req_kwargs = {
            'headers': HEADERS,
            'auth': ""
            }

    if data:
        req_kwargs['json'] = data

    try:
        return requests.request(method, url, **req_kwargs)
    except requests.exceptions.ConnectionError as e:
        logger.error(f'unable to connect to elasticsearch: {str(e)}')
        r = Response()
        r.status_code = 503
        r.headers['content-type'] = 'application/json'
        r._content = '{"error": "resource temporarily unavailable"}'.encode()
        r.encoding = 'utf8'
        return r


def get_index_templates():
    template_files = glob.glob(TEMPLATES_DIR+"*.json")

    templates = []
    for tf in template_files:
        f = open(tf)
        template = json.load(f)
        f.close()
        templates.append((template['name'], template['template']))

    return templates
