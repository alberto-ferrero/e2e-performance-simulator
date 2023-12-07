#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

""" E2E Performance Simulator Flight Dynamics Provider Handler: REST API Requests """

from ..utils.results import AppResult
import requests
import json

def propagate(url: str, propagationRequest: dict) -> dict:
    """ Call the Flight Dynamics Provider and get propagation data """
    payload = json.dumps(propagationRequest)
    response = requests.request("POST", url,
                                headers={'Content-Type': 'application/json'},
                                params={'format': 'FULL'},
                                data=payload).json()
    if 'status' in response:
        return AppResult(response['status'], propagationRequest, response['error'])
    else:
        return AppResult(200, propagationRequest, response)
    
# -*- coding: utf-8 -*-