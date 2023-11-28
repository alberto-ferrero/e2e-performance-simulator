#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

import os
import glob
import time
import datetime

import geopandas as gpd
import matplotlib.pyplot as plt
import pymap3d as pm
from PIL import Image

#HACK ignoring all conversion and deprecations WARNINGS
import warnings
warnings.simplefilter(action='ignore')

import pandas as pd
import numpy as np

from ..analysis.utils import getFlatXConnections, getItalXConnections
from ....utils.filemanager import makeOutputFolder

#Import docx
from docx import Document

#Constants
Re = 6371000     #[m]
c = 299792458    #[m/s]
deltaAngle = 5   #[deg]
j2000Date = datetime.datetime(2000, 1, 1)

""" E2E Performance Simulator Analysis: Latency """

def write(doc: Document, outputDataFolderPath: str, outputPlotFolderPath: str, flightDynamicsDataOutputPath: str):
    tick = time.time()
    #Read from Flight Dynamics file and extract EME2000 coordinates
    satsDf = {}
    for fileName in glob.glob(os.path.join(flightDynamicsDataOutputPath, "*_orbit-state.csv")):
        satId = fileName.split(os.sep)[-1].split("_")[0]
        df = pd.read_csv(fileName)
        df = df[['utcTime', 'X', 'Y', 'Z']].iloc[0:1]
        satsDf[satId] = df

    if satsDf == {}:
        return
    
    outputAnalysFolderPath = os.path.join(outputDataFolderPath, 'analysis')
    makeOutputFolder(outputAnalysFolderPath)

    tmpPath = os.path.join(outputPlotFolderPath, 'tmp')
    makeOutputFolder(tmpPath)

    #Write section       
    doc.add_heading("Signal Latency", 1)
    
    #Iterate considering both meshes
    lats = np.arange(-90, 90 + deltaAngle / 2.0, deltaAngle)
    lngs = np.arange(-180, 180 + deltaAngle / 2.0, deltaAngle)
    for getMesh, tag in ((getFlatXConnections, 'Flat X'), (getItalXConnections, 'Ital X')):
        images = []
        #Move around globe from focal point and calculate transmission based on speed of light
        latitudes = np.arange(0, 95, 5)
        for latitude in latitudes:
            longitude = 0
            firstGeoPoint = getPointFromLatLong(latitude, longitude)

            #Get first communication distance
            firstDistance, firstSatId = getCloserSatelliteDistance(satsDf, firstGeoPoint)
            firstDelay = firstDistance / c

            #Empty delays
            delays = np.empty(shape=(len(lats), len(lngs)))
        
            #Get closer satellite distance and calculate delay as d * c
            for i, lat in enumerate(lats):
                for j, lng in enumerate(lngs):
                    geoPoint = getPointFromLatLong(lat, lng)
                    distance, closerSatId = getCloserSatelliteDistance(satsDf, geoPoint)
                    #Go through mesh from initial geo point up to target point
                    nextSatId = closerSatId
                    contactedSatIds = []
                    #[DEBUG]print("\n", lat, lng, "from SAT", closerSatId, "to SAT", firstSatId)
                    while True and nextSatId != firstSatId:
                        #From the current point, amongh the ones in the mesh, get closer to initial geo point
                        closerSatId = getCloserSatelliteDistanceMesh(getMesh, satsDf, firstGeoPoint, contactedSatIds + [nextSatId,])
                        #[DEBUG]print(nextSatId, [satId for satId in getMesh(nextSatId) if satId not in contactedSatIds], 'closer', closerSatId)
                        contactedSatIds.append(closerSatId)
                        #Add intersatellite distance and go to next
                        distance += getDistance(getSatellitePosition(satsDf[closerSatId]),
                                                getSatellitePosition(satsDf[nextSatId]))
                        nextSatId = closerSatId
                    delays[i][j] =  (distance / c + firstDelay) * 1000.0 #to [millis]
            
            #Build heat map
            worldmap = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
            fig, ax = plt.subplots()
            worldmap.plot(color="darkgrey", ax=ax)
            cs = ax.contourf(lngs, lats, delays, alpha=0.3)
            cf = fig.colorbar(cs, fraction=0.046, pad=0.04)
            cf.ax.set_ylabel("Latency [millis]", loc='center')
            ax.set_xlabel("Longitude [deg]")
            ax.set_ylabel("Latitude [deg]")
            ax.set(xlim=[lngs[0], lngs[-1]], ylim=[lats[0], lats[-1]])
            for satId in satsDf:
                lat, lng = getSatelliteLatitudeLongitude(satsDf[satId])
                ax.scatter(lng, lat, s=10, c=['black'], alpha=0.7)
            ax.scatter(longitude, latitude, s=30, c=['red'], alpha=0.9)
            ax.annotate("UT", (longitude, latitude))
            if latitude == 0:
                #Save
                pd.DataFrame(delays, columns=lngs, index=lats).to_csv(os.path.join(outputAnalysFolderPath, 'analysis_latency-{}-mesh.csv'.format(tag)))
                figPath = os.path.join(outputPlotFolderPath, "analysis_latency-{}-mesh.jpg".format(tag.replace(" ", "")))
                fig.savefig(figPath, bbox_inches='tight')
                doc.add_paragraph('The picture below shows signal delay in milliseconds, from an user terminal set at Latitude {} deg, Longitude {} deg, for {} mesh geometry'.format(latitude, longitude, tag))
                p = doc.add_paragraph()
                r = p.add_run()
                r.add_picture(figPath)

            ax.set_title("Lat = {} deg".format(latitude))
            figTmpPath = os.path.join(tmpPath, "analysis_latency-{}-mesh-{}.jpg".format(tag.replace(" ", ""), latitude))
            fig.savefig(figTmpPath, bbox_inches='tight')
            images.append(figTmpPath)

        #Save gif
        frames = [Image.open(image) for image in images]
        frame = frames[0]
        frame.save(os.path.join(outputPlotFolderPath, 'analysis_latency-{}-mesh.gif'.format(tag)), 
                    format="GIF", append_images=frames,
                    save_all=True, duration=100, loop=0)
    
    doc.add_page_break()
    print('   - Added section on User Signal Latency in {:.4f} seconds'.format(time.time() - tick))

def getPointFromLatLong(lat: float, lng: float) -> np.array:
    """ From lat and lng ([deg]) get geo point, considering perfect sphere, alt 0     
    """
    x, y, z = pm.geodetic2eci(lat, lng, 0, j2000Date)
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
    return np.degrees(np.arcsin(pos[2] / np.linalg.norm(pos))) , np.degrees(np.arctan2(pos[1], pos[0]))

def getCloserSatelliteDistanceMesh(getMesh, satsDf: dict, geoPoint: np.array, contactedSatIds: list) -> (float, str):
    """ Iterate 1 step into mesh, get for each of the connected satellites, the next closer and choose the one with less distance as root point """
    subSatsDf = getMeshSatsDataframe(getMesh, satsDf, contactedSatIds)
    #Get distance over mesh
    distances = {}
    for satId in subSatsDf:
        pos = getSatellitePosition(satsDf[satId])
        d = getDistance(pos, geoPoint)
        nextSubSatsDf = getMeshSatsDataframe(getMesh, satsDf, contactedSatIds + [satId,])
        #Get closer in next step and add to distance
        dd, _ = getCloserSatelliteDistance(nextSubSatsDf, geoPoint)
        distances[dd+d] = satId
    #Get closer
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