#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

""" E2E Performance Simulator Flight Dynamics Provider Handler REST API Requests """

from ..utils.results import AppResult
import requests
import json

#Constants
ENDPOINT = "/api/v1/propagation-data"
N_MAX_SATS = 20

def propagate(serviceUrl: str, propagationRequest: dict) -> dict:
    """ Call the Flight Dynamics Provider and get propagation data """
    serviceUrl = serviceUrl + '/' if serviceUrl[-1] != '/' else serviceUrl
    url = serviceUrl + 'api/v1/propagation-data'
    
    #Propagate and return propagation data, cutting run to not overkill memory
    propagationData = {}
    nSats = len(propagationRequest['assets'])

    for ii in range(int(nSats / N_MAX_SATS)):
        #Get batch of assets, call app and get results
        subPropagationRequest = getSubSetPropagationRequest(propagationRequest, ii * N_MAX_SATS, ((ii + 1) * N_MAX_SATS) - 1)
        res: AppResult = callServer(url, subPropagationRequest)
        propagationData.update(res.result)
        
    if nSats % N_MAX_SATS != 0:
        # Get batch of assets, call app and get results
        subPropagationRequest = getSubSetPropagationRequest(propagationRequest, int(nSats / N_MAX_SATS) * N_MAX_SATS, int(nSats / N_MAX_SATS) * N_MAX_SATS + nSats % N_MAX_SATS)
        res: AppResult = callServer(url, subPropagationRequest)
        propagationData.update(res.result)
    
    return AppResult(200, propagationData)

def getSubSetPropagationRequest(propagationRequest: dict, idxi: int, idf: int) -> dict:
    #Get batch of assets
    subPropagationRequest = {}
    subPropagationRequest['scenario'] = propagationRequest['scenario']
    subPropagationRequest['assets'] = propagationRequest['assets'][idxi:idf]
    subPropagationRequest['pointsOfInterest'] = propagationRequest['pointsOfInterest']
    return subPropagationRequest

def callServer(url: str, propagationRequest: dict) -> AppResult:
    #Call Server
    
    payload = json.dumps(propagationRequest)
    response = requests.request("POST", url,
                                headers={'Content-Type': 'application/json'},
                                params={'format': 'FULL'},
                                data=payload).json()
    if 'status' in response:
        return AppResult(response['status'], response['error'])
    else:
        return AppResult(200, response)
    
# -*- coding: utf-8 -*-