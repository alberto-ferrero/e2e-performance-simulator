#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

""" E2E Performance Simulator Space Link Budget Calculator Handler: REST API Requests """

from ..utils.results import AppResult
from ..spacelink.mapper import getSatelliteOpticalLinkProperties

import pandas as pd

import requests
import json

def spacelink(url: str, spaceLinkRequest: dict) -> dict:
    """ Call the Space Link Budget Calculator and get link data """
    return AppResult(200, spaceLinkRequest, {spaceLinkRequest['satellite']['id']: [{"margin": 2}, {"margin": 3}]})
    #TODO
    payload = json.dumps(spaceLinkRequest)
    response = requests.request("POST", url,
                                headers={'Content-Type': 'application/json'},
                                data=payload).json()
    if 'status' in response:
        return AppResult(response['status'], spaceLinkRequest, response['error'])
    else:
        return AppResult(200, spaceLinkRequest, response)

def getSpaceLinkRequest(satId: str, satStatesDf: dict, contactsDf: pd.DataFrame) -> dict:
    """ For couple Satellite-Satellite, get all satellite states in between contacts, and assets communication properties """
    spaceLinkRequest = {}
    spaceLinkRequest = {}
    if len(contactsDf) > 0:
        #Build satellite object with link properties
        spaceLinkRequest['satellite'] = {}
        spaceLinkRequest['satellite']['id'] = satId
        spaceLinkRequest['satellite']['oisl'] = getSatelliteOpticalLinkProperties()
        # Get states for each contact window
        spaceLinkRequest['satellite']['states'] = getContactStates(satId, satStatesDf, contactsDf)
    return spaceLinkRequest

def getContactStates(satId: str, satStatesDf: dict, soiContacts: pd.DataFrame) -> list:
    def getDistancesOfDeputy(soiIds: list, satsStates: dict, timestamp: int, pos: tuple):
        distances = {}
        for soiId in soiIds:
            df = satsStates[soiId]
            deputyState = df[df['timestamp'] == timestamp]
            if len(deputyState) == 1:
                distances[soiId] = getDistance(pos[0], pos[1], pos[2], deputyState.iloc[0]['X'], deputyState.iloc[0]['Y'], deputyState.iloc[0]['Z'])
        return distances

    soiIds = soiContacts['argumentOfInterestId'].unique().tolist()
    states: pd.DataFrame = satStatesDf[satId]
    #Build intervals
    intervals = [pd.Interval(soiContacts.iloc[i]['startTimestamp'], soiContacts.iloc[i]['endTimestamp'], 'both') for i in range(len(soiContacts))]
    #Get states inside intervales
    mask = states['timestamp'].apply(lambda x: any([x in interval for interval in intervals]))
    filteredStates = states[mask]
    filteredStates = filteredStates[['utcTime', 'timestamp', 'X', 'Y', 'Z']]
    #Get for each states into a ISV contact, the distance of deputy satellites, if position known
    filteredStates["distances"] = filteredStates.apply(lambda s: getDistancesOfDeputy(soiIds, satStatesDf, s["timestamp"], (s["X"], s["Y"], s["Z"])), axis=1)
    return filteredStates.T.apply(lambda x: x.dropna().to_dict()).tolist()

def getDistance(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float) -> float:
    """ Get distance between componenst of 2 3D vectors """
    from math import sqrt
    return sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2) + (z1 - z2) * (z1 - z2))

# -*- coding: utf-8 -*-
