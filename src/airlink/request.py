#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

""" E2E Performance Simulator Air Link Budget Calculator Handler: REST API Requests """

from ..utils.results import AppResult
import pandas as pd
import requests
import json

def airlink(url: str, airLinkRequest: dict) -> dict:
    """ Call the Air Link Budget Calculator and get link data """
    payload = json.dumps(airLinkRequest)
    response = requests.request("POST", url,
                                headers={'Content-Type': 'application/json'},
                                data=payload).json()
    if 'status' in response:
        return AppResult(response['status'], airLinkRequest, response['error'])
    else:
        return AppResult(200, airLinkRequest, response)

def getAirLinkRequest(satId: str, satelliteAntennaProperties: dict, statesDf: pd.DataFrame, contactsDf: pd.DataFrame, antennaId: str, antennaLocation: dict, antennatProperties: dict) -> dict:
    """ For couple Satellite-GroundPoint, get all satellite states in between contacts, and assets communication properties """
    airLinkRequest = {}
    poiContactsDf = contactsDf[contactsDf['argumentOfInterestId'] == antennaId]
    airLinkRequest = {}
    if len(poiContactsDf) > 0:
        # Build Point of Interest (poi) properties
        airLinkRequest['ground'] = {}
        airLinkRequest['ground']['id'] = antennaId
        airLinkRequest['ground']['location'] = antennaLocation
        airLinkRequest['ground']['antenna'] = antennatProperties
        # Build satellite object with link properties
        airLinkRequest['satellite'] = {}
        airLinkRequest['satellite']['id'] = satId
        airLinkRequest['satellite']['antenna'] = satelliteAntennaProperties
        # Get states for each contact window
        airLinkRequest['satellite']['states'] = getContactStates(poiContactsDf, statesDf)
    return airLinkRequest

def getContactStates(poiContacts: pd.DataFrame, states: pd.DataFrame) -> list:
    #Build intervals
    intervals = [pd.Interval(poiContacts.iloc[i]['startTimestamp'], poiContacts.iloc[i]['endTimestamp'], 'both') for i in range(len(poiContacts))]
    #Get states inside intervales
    mask = states['timestamp'].apply(lambda x: any([x in interval for interval in intervals]))
    filteredStates = states[mask]
    filteredStates = filteredStates[['utcTime', 'X', 'Y', 'Z']]
    return filteredStates.T.apply(lambda x: x.dropna().to_dict()).tolist()

# -*- coding: utf-8 -*-
