#
# encoding: utf-8
#
# This module contains utility functions to automatically install Rocket Search for Elasticsearch
# and functions to check the installation.
#
# devs@droxit.de
#
# Copyright (c) 2019 droxIT GmbH
#

import time
import logging
import sys

from utils.elasticsearch import get_index_templates, es_request
from utils.json_utils import compare_jsons

ES_URL = "http://localhost:9200/"
HEADER = {"content-type": "application/json"}
logger = logging.getLogger(__name__)


def check_templates():
    logger.info("Checking for correctly installed Rocket Search templates for Elasticsearch.")
    templates = get_index_templates()

    for (name, template) in templates:
        url = ES_URL + "_template/{}".format(name)
        installed_template = es_request("GET", url, {}).json().get(name)
        eq = compare_jsons(template, installed_template)

        if eq:  # templates match, check if all indices exist
            for index in template.get("index_patterns"):
                index_url = ES_URL + index
                r = es_request("HEAD", index_url, {})  # check if exits

                if r.status_code == 404:
                    logger.info("Index {} does not exist, creating {}...".format(index, index))
                    r = es_request("PUT", index_url, {})
                    if r.status_code not in [200, 201]:
                        logger.error(
                            "{}: could not create index {}, error: {}".format(r.status_code, index, r.content))

            logger.info("Template {} is up to date".format(name))

        else:  # delete indices if templates do not match
            logger.info("Template '{}' was not up to date. Updating ...".format(name))

            if installed_template:  # delete indices and create new ones
                index_patterns = installed_template.get("index_patterns")
                if not index_patterns:
                    logger.debug("No indices in installed template '{}'".format(index_patterns))
                for index in index_patterns:
                    delete_es_index_if_exists(index)
                # delete installed template
                logger.info("Deleting installed template '{}'...".format(name))
                r = es_request("DELETE", url)
                if r.status_code > 300:
                    logger.error("Could not delete template '{}'.".format(name))

            r = es_request("PUT", url, template)

            if r.status_code in [200, 201]:
                for index in template.get("index_patterns"):  # create new indices
                    index_url = ES_URL + index
                    r = es_request("HEAD", index_url, {})  # check if exits

                    if r.status_code == 404:
                        r = es_request("PUT", index_url, {})
                        if r.status_code not in [200, 201]:
                            logger.error(
                                "{}: could not create index {}, error: {}".format(r.status_code, index, r.content))
                logger.info("Successfully updated template '{}'.".format(name))
            else:
                logger.error("{}: Updating template '{}' failed, error: {}".format(r.status_code, template, r.content))


def check_es_connection():
    url = ES_URL
    logger.info("Trying to connect to Elasticsearch instance running on {}.".format(url))

    success = False
    tries_left = 10

    while not success and tries_left > 0:
        r = es_request("GET", url, {})
        if r.status_code in [200, 201]:
            success = True
        else:
            success = False

        if not success:
            logger.error("Connection to Elasticsearch instance failed on {}. Trying again.".format(url))
            tries_left -= 1
            time.sleep(5)

    if success:
        logger.info("Connection to Elasticsearch instance established on {}.".format(url))
        return True
    else:
        logger.error("Unable to establish connection to Elasticsearch instance on {}.".format(url))
        return False


def create_es_index(index_name):
    r = es_request("PUT", ES_URL + index_name)

    if r.status_code >= 300:
        logger.error("Unable to create index: {}".format(r.json()))
        return False
    else:
        return True


def delete_es_index_if_exists(index_name):
    index_url = ES_URL + index_name
    # check if index exists, then delete it
    r = es_request("HEAD", index_url, {})
    if r.status_code == 200:
        r = es_request("DELETE", index_url)
        if r.status_code in [200, 201]:
            logger.info("Deleted index '{}'...".format(index_name))
        else:
            logger.error("{}: could not delete index '{}', error: {}".format(r.status_code, index_name, r.content))


if __name__ == "__main__":
    # Attention: Indices with updated templates will be deleted
    alive = check_es_connection()
    if not alive:
        sys.exit(1)
    check_templates()
    print("Successfully added templates.")
