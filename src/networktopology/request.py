#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

""" E2E Performance Simulator Network Topology Handler: REST API Requests """

from ..utils.results import AppResult
import requests
import json

def network(url: str, networkRequest: dict) -> dict:
    """ Call the Network Topology mapper and get network data """
    payload = json.dumps(networkRequest)
    response = requests.request("POST", url,
                                headers={'Content-Type': 'application/json'},
                                data=payload).json()
    if 'status' in response:
        return AppResult(response['status'], networkRequest, response['error'])
    else:
        return AppResult(200, networkRequest, response)
    
# -*- coding: utf-8 -*-