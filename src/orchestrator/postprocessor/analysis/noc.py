#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

import pymap3d as pm
import numpy as np

from ....utils.timeconverter import getDatetimeFromDate

""" E2E Performance Simulator Analysis: utilty methods """

def getItalXConnections(satId: str) -> list:
    """ Get Ital X connection, based on satellite id rsn-sat-#plane-#sat-#satXplane-#planes"""
    rsn, satId, plane, sat, totSats, totPlanes = satId.split("-")

    planeM = str(int(plane) - 1 if int(plane) - 1 >= 0 else int(totPlanes) - 1)
    planeP = str(int(plane) + 1 if int(plane) + 1 < int(totPlanes) else 0)

    satM = str(int(sat) - 1 if int(sat) - 1 >= 0 else int(totSats) - 1)
    satP = str(int(sat) + 1 if int(sat) + 1 < int(totSats) else 0)
    satMM = sat
    satPP = sat
    
    #Check border connections between upstream/downstream
    if int(plane) == int(totPlanes) - 1:
        satPP = str(int(int(totSats) / 2) - int(sat) if int(int(totSats) / 2) - int(sat) >= 0 else int(int(totSats) / 2) - int(sat) + int(totSats))
    elif int(plane) == 0:
        satMM = str(int(int(totSats) / 2) - int(sat) if int(int(totSats) / 2) - int(sat) >= 0 else int(int(totSats) / 2) - int(sat) + int(totSats))
    
    return ("-".join([rsn, satId, plane,  satP,  totSats, totPlanes]),
            "-".join([rsn, satId, plane,  satM,  totSats, totPlanes]),
            "-".join([rsn, satId, planeM, satMM, totSats, totPlanes]),
            "-".join([rsn, satId, planeP, satPP, totSats, totPlanes]))

def getFlatXConnections(satId: str) -> list:
    """ Get Flat X connection, based on satellite id rsn-sat-#plane-#sat-#satXplane-#planes"""
    # print(satId)
    rsn, satId, plane, sat, totSats, totPlanes = satId.split("-")
    
    planeM = str(int(plane) - 1 if int(plane) - 1 >= 0 else int(totPlanes) - 1)
    planeP = str(int(plane) + 1 if int(plane) + 1 < int(totPlanes) else 0)
    
    satPP = str(int(sat) + 1 if int(sat) + 1 < int(totSats) else 0)
    satMP = str(int(sat) - 1 if int(sat) - 1 >= 0 else int(totSats) - 1)
    satM = sat
    satP = sat

    #Check border connections between upstream/downstream
    if int(plane) == int(totPlanes) - 1:
        satPP = str(int(int(totSats) / 2) - 1 - int(sat) if int(int(totSats) / 2) - 1 - int(sat) >= 0 else int(int(totSats) / 2) - 1 - int(sat) + int(totSats))
        satP = str(int(int(totSats) / 2) - int(sat) if int(int(totSats) / 2) - int(sat) >= 0 else int(int(totSats) / 2) - int(sat) + int(totSats))
    elif int(plane) == 0:
        satMP = str(int(int(totSats) / 2) - 1 - int(sat) if int(int(totSats) / 2) - 1 - int(sat) >= 0 else int(int(totSats) / 2) - 1 - int(sat) + int(totSats))
        satM = str(int(int(totSats) / 2) - int(sat) if int(int(totSats) / 2) - int(sat) >= 0 else int(int(totSats) / 2) - int(sat) + int(totSats))

    return ("-".join([rsn, satId, planeM, satM,  totSats, totPlanes]),
            "-".join([rsn, satId, planeM, satMP, totSats, totPlanes]),
            "-".join([rsn, satId, planeP, satP,  totSats, totPlanes]),
            "-".join([rsn, satId, planeP, satPP, totSats, totPlanes]))

def getPointFromLatLong(lat: float, lng: float, time) -> np.array:
    """ From lat and lng ([deg]) get geo point, considering perfect sphere, alt 0     
    """
    x, y, z = pm.geodetic2eci(lat, lng, 0, time)
    return np.array((x, y, z))

def getDistance(a, b) -> float:
    return np.linalg.norm(a-b)

def getMeshSatsDataframe(getMesh, satsDf: dict, contactedSatIds: list) -> dict:
    nextSatId = contactedSatIds[-1]
    #Get mesh satellites, not passing from the onese already contacted
    meshSatsIds = getMesh(nextSatId)
    meshSatsIds = [satId for satId in meshSatsIds if satId not in contactedSatIds]
    meshDf = {}
    for satId in meshSatsIds:
        if satId not in satsDf:
            raise Exception('ERROR: mesh satellite {} was not propagated, not found in Propagation Data'.format(satId))
        meshDf[satId] = satsDf[satId]
    return meshDf

def getSatellitePosition(df) -> np.array:
    return np.array((df.iloc[0]['X'], df.iloc[0]['Y'], df.iloc[0]['Z']))

def getSatelliteLatitudeLongitude(df) -> (float, float):
    pos: np.array = getSatellitePosition(df)
    lla = pm.eci2geodetic(pos[0], pos[1], pos[2], getDatetimeFromDate(df.iloc[0]['utcTime']))
    return lla[0], lla[1]

def getCloserSatelliteDistanceMesh(getMesh, satsDf: dict, geoPoint: np.array, contactedSatIds: list, firstSatId: str) -> (float, str):
    """ Iterate 1 step into mesh, get for each of the connected satellites, the next closer and choose the one with less distance as root point """
    subSatsDf = getMeshSatsDataframe(getMesh, satsDf, contactedSatIds)
    if firstSatId in subSatsDf:
        return firstSatId
    #Get distance over mesh
    distances = {}
    for satId in subSatsDf:
        pos = getSatellitePosition(satsDf[satId])
        d = getDistance(pos, geoPoint)
        nextSubSatsDf = getMeshSatsDataframe(getMesh, satsDf, contactedSatIds + [satId,])
        #Get closer in next step and add to distance
        dd, _ = getCloserSatelliteDistance(nextSubSatsDf, geoPoint)
        distances[dd+d] = satId
    #Get closer satId as distance: satId
    return distances[min(distances.keys())]

def getCloserSatelliteDistance(satsDf: dict, geoPoint: np.array) -> (float, str):
    """ Iterate over entire list of satellites and get closer """
    from sys import maxsize
    minD = maxsize
    minSatId = ""
    for satId in satsDf.keys():
        pos = getSatellitePosition(satsDf[satId])
        d = getDistance(pos, geoPoint)
        if d < minD:
            minSatId = satId
            minD = d
    return minD, minSatId

# -*- coding: utf-8 -*-