#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

import pymap3d as pm
import numpy as np

from ....utils.timeconverter import getDatetimeFromDate

""" E2E Performance Simulator Analysis: utilty methods """

def getItalXConnections(satId: str, totPlanes: int, totSats: int) -> list:
    """ Get Ital X connection, based on satellite id rsn-P#plane-#sat """
    rsn, constellation, plane, index = satId.split("-")

    plane = int(plane.replace('P', ''))
    index = int(index)

    planeL = str(plane - 1 if plane - 1 > 0 else int(totPlanes))
    planeR = str(plane + 1 if plane + 1 <= int(totPlanes) else 1)

    #Even plane
    indexLU = getPlusIndex(index, totSats)
    indexRU = getSameIndex(index, totSats)
    indexLL = getSameIndex(index, totSats)
    indexRL = getMinusIndex(index, totSats)

    #Even plane
    if int(plane) % 2 == 0:
        if plane == totPlanes:
            indexRU = getPlusIndex(index, totSats, True, -1)
    #Odd plane
    else:
        if plane == totPlanes:
            indexRU = getPlusIndex(index, totSats, True, +1)
        elif plane == 1:
            indexLL = getPlusIndex(index, totSats, True, +2)

    #To string
    plane = str(int(plane))
    index = str(int(index))
    indexLU = str(int(indexLU))
    indexRU = str(int(indexRU))
    indexLL = str(int(indexLL))
    indexRL = str(int(indexRL))

    return ("-".join([rsn, constellation, 'P' + plane.replace('P', '').zfill(2),  indexLU.zfill(2)]),
            "-".join([rsn, constellation, 'P' + plane.replace('P', '').zfill(2),  indexRL.zfill(2)]),
            "-".join([rsn, constellation, 'P' + planeL.zfill(2), indexLL.zfill(2)]),
            "-".join([rsn, constellation, 'P' + planeR.zfill(2), indexRU.zfill(2)]))

def getFlatXConnections(satId: str, totPlanes: int, totSats: int) -> list:
    """ Get Flat X connection, based on satellite id rsn-P#plane-#sat """
    rsn, constellation, plane, index = satId.split("-")

    plane = int(plane.replace('P', ''))
    index = int(index)

    planeL = str(plane - 1 if plane - 1 > 0 else int(totPlanes))
    planeR = str(plane + 1 if plane + 1 <= int(totPlanes) else 1)

    #Even plane
    if int(plane) % 2 == 0:
        indexLU = getPlusIndex(index, totSats)
        indexRU = getPlusIndex(index, totSats)
        indexLL = getSameIndex(index, totSats)
        indexRL = getSameIndex(index, totSats)

        if plane == totPlanes:
            indexRL = getMinusIndex(index, totSats, True, -2)
            indexRU = getMinusIndex(index, totSats, True, -1)

    #Odd plane
    else:
        indexLU = getSameIndex(index, totSats)
        indexRU = getSameIndex(index, totSats)
        indexLL = getMinusIndex(index, totSats)
        indexRL = getMinusIndex(index, totSats)

        if plane == totPlanes:
            indexRL = getSameIndex(index, totSats, True, -1)
            indexRU = getPlusIndex(index, totSats, True, -1)
        elif plane == 1:
            indexLL = getSameIndex(index, totSats, True, -2)
            indexLU = getPlusIndex(index, totSats, True, -2)

    #To string
    plane = str(int(plane))
    index = str(int(index))
    indexLU = str(int(indexLU))
    indexRU = str(int(indexRU))
    indexLL = str(int(indexLL))
    indexRL = str(int(indexRL))

    return ("-".join([rsn, constellation, 'P' + planeL.zfill(2), indexLU.zfill(2)]),
            "-".join([rsn, constellation, 'P' + planeL.zfill(2), indexLL.zfill(2)]),
            "-".join([rsn, constellation, 'P' + planeR.zfill(2), indexRU.zfill(2)]),
            "-".join([rsn, constellation, 'P' + planeR.zfill(2), indexRL.zfill(2)]))

def getPlusIndex(index: int, totSats: int, reversed = False, deltaIndex = 0) -> int:
    if reversed:
        index += deltaIndex
        return totSats / 2 - index + 1 if totSats / 2 - index + 1 > 0 else totSats / 2 - index + 1 + totSats
    else:
        return index + 1 if index + 1 <= totSats else 1
    
def getMinusIndex(index: int, totSats: int, reversed = False, deltaIndex = 0) -> int:
    if reversed:
        index += deltaIndex
        return totSats / 2 - index - 1 if totSats / 2 - index - 1 > 0 else totSats / 2 - index - 1 + totSats
    else:
        return index - 1 if index - 1 > 0 else totSats
    
def getSameIndex(index: int, totSats: int, reversed = False, deltaIndex = 0) -> int:
    if reversed:
       index += deltaIndex
       return totSats / 2 - index if totSats / 2 - index > 0 else totSats / 2 - index + totSats
    else:
        return index

def getPointFromLatLong(lat: float, lng: float, time) -> np.array:
    """ From lat and lng ([deg]) get geo point, considering perfect sphere, alt 0     
    """
    x, y, z = pm.geodetic2eci(lat, lng, 0, time)
    return np.array((x, y, z))

def getDistance(a, b) -> float:
    return np.linalg.norm(a-b)

def getMeshSatsDataframe(getMesh, totPlanes: int, totSats: int, satsDf: dict, contactedSatIds: list) -> dict:
    satId = contactedSatIds[-1]
    #Get mesh satellites, not passing from the onese already contacted
    meshSatsIds = getMesh(satId, totPlanes, totSats)
    meshSatsIds = [satId for satId in meshSatsIds if satId not in contactedSatIds]
    meshDf = {}
    for meshSatId in meshSatsIds:
        if meshSatId not in satsDf:
            raise Exception('ERROR: for satellite {}, mesh satellite {} was not propagated, not found in Propagation Data'.format(satId, meshSatId))
        meshDf[meshSatId] = satsDf[meshSatId]
    return meshDf

def getSatellitePosition(df, index=0) -> np.array:
    return np.array((df.iloc[index]['X'], df.iloc[index]['Y'], df.iloc[index]['Z']))

def getSatellitePositionVelocity(df, index) -> np.array:
    return np.array((df.iloc[index]['X'], df.iloc[index]['Y'], df.iloc[index]['Z'], df.iloc[index]['Vx'], df.iloc[index]['Vy'], df.iloc[index]['Vz']))

def getSatelliteLatitudeLongitude(df, index = 0) -> (float, float):
    pos: np.array = getSatellitePosition(df, index)
    lla = pm.eci2geodetic(pos[0], pos[1], pos[2], getDatetimeFromDate(df.iloc[index]['utcTime']))
    return lla[0], lla[1]

def getCloserSatelliteDistanceMesh(getMesh, totPlanes: int, totSats: int, satsDf: dict, geoPoint: np.array, contactedSatIds: list, firstSatId: str) -> (float, str):
    """ Iterate 1 step into mesh, get for each of the connected satellites, the next closer and choose the one with less distance as root point """
    subSatsDf = getMeshSatsDataframe(getMesh, totPlanes, totSats, satsDf, contactedSatIds)
    if firstSatId in subSatsDf:
        return firstSatId
    #Get distance over mesh
    distances = {}
    for satId in subSatsDf:
        pos = getSatellitePosition(satsDf[satId])
        d = getDistance(pos, geoPoint)
        nextSubSatsDf = getMeshSatsDataframe(getMesh, totPlanes, totSats, satsDf, contactedSatIds + [satId,])
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