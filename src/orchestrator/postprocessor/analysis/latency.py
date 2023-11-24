#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

import os
import glob
import time
from math import radians

import geopandas as gpd
import matplotlib.pyplot as plt

#HACK ignoring all conversion and deprecations WARNINGS
import warnings
warnings.simplefilter(action='ignore')

import pandas as pd
import numpy as np

from ..analysis.utils import getFlatXConnections, getItalXConnections

#Import docx
from docx import Document

#Constants
Re = 6371000     #[m]
c = 299792458    #[m/s]
deltaAngle = 3   #[deg]

""" E2E Performance Simulator Analysis: Latency """

def write(doc: Document, outputPlotFolderPath: str, flightDynamicsDataOutputPath: str):
    tick = time.time()
    #Read from Flight Dynamics file and extract EME2000 coordinates
    constDf = {}
    for fileName in glob.glob(os.path.join(flightDynamicsDataOutputPath, "*_orbit-state.csv")):
        satId = fileName.split(os.sep)[-1].split("_")[0]
        df = pd.read_csv(fileName)
        df = df[['utcTime', 'X', 'Y', 'Z']].iloc[0:1]
        constDf[satId] = df

    if constDf == {}:
        return
    
    #Write section       
    doc.add_heading("Signal Latency", 1)
    
    #Move around globe, from Lat 0 deg, Lng 0 deg and calculate transmission based on speed of light
    latitude = 0
    longitude = 0
    firstGeoPoint = getPointFromLatLong(latitude, longitude)

    #Get first communication distance
    firstDistance, firstSatId = getCloserSatelliteDistance(constDf, firstGeoPoint)
    firstDelay = firstDistance * c
    
    #Iterate considering both meshes
    lats = np.arange(-90, 90, deltaAngle)
    lngs = np.arange(-180, 180, deltaAngle)
    delays = np.empty(shape=(len(lats), len(lngs)))
    for getMesh, tag in ((getFlatXConnections, 'Flat X'), (getItalXConnections, 'Ital X')):
        #Get closer satellite distance and calculate delay as d * c
        for i, lat in enumerate(lats):
            for j, lng in enumerate(lngs):
                geoPoint = getPointFromLatLong(lat, lng)
                distance, closerSatId = getCloserSatelliteDistance(constDf, geoPoint)
                #Go through mesh from first point up to target point
                nextSatId = firstSatId
                while True and nextSatId != closerSatId:
                    #Get mesh satellites
                    meshSatsIds = getMesh(nextSatId)
                    print(nextSatId, meshSatsIds)
                    subConstDf = getMeshDataframe(constDf, meshSatsIds)
                    #Amongh the ones in the mesh, get closer
                    _, satId = getCloserSatelliteDistance(subConstDf, geoPoint)
                    #Check arrived to target satellite
                    if nextSatId == closerSatId:
                        break
                    else:
                        #Add intersatellite distance and go to next
                        distance += getDistance(getSatellitePosition(constDf[satId]),
                                                getSatellitePosition(constDf[nextSatId]))
                        nextSatId = satId

                delays[i][j] =  (distance * c + firstDelay) * 1000.0 #to [millis]
            print(lat)
 
        #Build heat map
        worldmap = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
        fig, ax = plt.subplots()
        worldmap.plot(color="lightgrey", ax=ax)
        ax.contourf(lngs, lats, delays, cmap='Spectral_r',extend='both')
        ax.set_xlabel("Longitude [deg]")
        ax.set_ylabel("Latitude [deg]")
        ax.set(xlim=[lngs[0], lngs[-1]], ylim=[lats[0], lats[-1]])
        for satId in constDf:
          lat, lng = getSatelliteLatitudeLongitude(constDf[satId])
          ax.scatter(lng, lat, s=40, c=['black'], alpha=0.9)
          ax.annotate(satId, (lng, lat))
        ax.text(1.15, 0.5, 'Latency [millis]', va='bottom', ha='center', rotation='vertical', rotation_mode='anchor', transform=ax.transAxes)
        figPath = os.path.join(outputPlotFolderPath, "analysis_latency-{}-mesh.png".format(tag.replace(" ", "")))
        fig.savefig(figPath,
                    bbox_inches='tight')

        doc.add_paragraph('The picture below shows signal delay in milliseconds, from an user terminal set at Latitude = 0 deg, Longitude = 0 deg, for {} mesh geometry'.format(tag))
        p = doc.add_paragraph()
        r = p.add_run()
        r.add_picture(figPath)

    doc.add_page_break()
    print(' - Added section on User Signal Latency in  {:.4f} seconds'.format(time.time() - tick))

def getPointFromLatLong(lat: float, lng: float) -> np.array:
    """ From lat and lng ([deg]) get geo point, considering perfect sphere, alt 0 m

        TO IMPROVE, add real Earth shape

        x = cos(lat) cos(lng)
        y = cos(lat) sin(lng)
        z = sin(lat)
    
    """
    lat = radians(lat)
    lng = radians(lng)
    return np.array((np.cos(lat) * np.cos(lng),
                     np.cos(lat) * np.sin(lng),
                     np.sin(lat)
                     )
                    )

def getDistance(a, b) -> float:
    return np.linalg.norm(a-b)

def getMeshDataframe(constDf: dict, satIds: list) -> dict:
    meshDf = {}
    for satId in satIds:
        if satId not in constDf:
            raise Exception('ERROR: mesh satellite {} has was not propagated, not in Propagation Data'.format(satId))
        meshDf[satId] = constDf[satId]
    return meshDf

def getSatellitePosition(df) -> np.array:
    return np.array((df.iloc[0]['X'], df.iloc[0]['Y'], df.iloc[0]['Z']))

def getSatelliteLatitudeLongitude(df) -> (float, float):
    pos: np.array = getSatellitePosition(df)
    return np.degrees(np.arcsin(pos[2] / np.linalg.norm(pos))) , np.degrees(np.arctan2(pos[1], pos[0]))

def getCloserSatelliteDistance(constDf: dict, geoPoint: np.array) -> (float, str):
    """ Iterate over entire list of satellites and get closer """
    from sys import maxsize
    minD = maxsize
    minSatId = ""
    for satId in constDf.keys():
        pos = getSatellitePosition(constDf[satId])
        d = getDistance(pos, geoPoint)
        if d < minD:
            minSatId = satId
            minD = d
    return minD, minSatId

# -*- coding: utf-8 -*-