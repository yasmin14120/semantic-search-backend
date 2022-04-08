#
# encoding: utf-8
#
# This module contains utility functions for handling JSON data.
#
# devs@droxit.de
#
# Copyright (c) 2019 droxIT GmbH
#


def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj


def compare_jsons(a: dict, b: dict):
    return ordered(a) == ordered(b)


def contains(a: dict, b: dict):
    keys = b.keys()
    for key in keys:
        a_value = a.get(key)
        b_value = b.get(key)

        if a_value is None:
            return False
        if isinstance(b_value, list):
            a_value.sort()
            b_value.sort()
            if a_value != b_value:
                return False
        elif isinstance(b_value, dict):
            contains(a_value, b_value)
        else:
            if a_value != b_value:
                return False
    return True
