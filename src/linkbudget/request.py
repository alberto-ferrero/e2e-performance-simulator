#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

""" E2E Performance Simulator Link Budget Calculator Handler: REST API Requests """

from ..utils.results import AppResult
import requests
import json

def link(url: str, linkRequest: dict) -> dict:
    """ Call the Link Budget Calculator and get link data """
    payload = json.dumps(linkRequest)
    response = requests.request("POST", url,
                                headers={'Content-Type': 'application/json'},
                                data=payload).json()
    if 'status' in response:
        return AppResult(response['status'], linkRequest, response['error'])
    else:
        return AppResult(200, linkRequest, response)
    
# -*- coding: utf-8 -*-