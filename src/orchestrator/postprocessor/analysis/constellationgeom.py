#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

import os
import glob
import time
import pandas as pd
from PIL import Image
from math import pi

from ....utils.filemanager import makeOutputFolder

#Import docx
from docx import Document

""" E2E Performance Simulator Analysis: Constellation Geometry """

def write(doc: Document, outputPlotFolderPath: str, flightDynamicsDataOutputPath: str):
    """Write analyis chapter """
    #Read from Flight Dynamics file and extract mean Keplerian elements
    tick = time.time()
    constDf = pd.DataFrame()
    satIds = []
    for fileName in glob.glob(os.path.join(flightDynamicsDataOutputPath, "*_bls-keplerian-state.csv")):
        df = pd.read_csv(fileName)
        satIds.append(fileName.split(os.sep)[-1].split("_")[0])
        df = df[['utcTime', 'rightAscensionAscendingNode', 'argumentPeriapsis', 'meanAnomaly']]
        try:
            constDf = pd.concat([constDf, df], axis=0)
        except:
            constDf = df

    if len(constDf) == 0:
        return

    #Get latitude argument (as eccentricity 0) 
    constDf['rightAscensionAscendingNode'] = constDf['rightAscensionAscendingNode'] * 180.0 / pi
    constDf['latitudeArgument'] = (constDf['argumentPeriapsis'] + constDf['meanAnomaly']) * 180.0 / pi
    constDf['latitudeArgument'] = constDf['latitudeArgument'].apply(lambda x: x - 360 if x >= 360 else x)
    
    #Get list of timestamps
    utcTimes = constDf['utcTime'].unique().tolist()

    #Save image for each time in tmp
    tmpPath = os.path.join(outputPlotFolderPath, 'tmp')
    makeOutputFolder(tmpPath)
    images = []
    deltaLa = 0
    firstLa = None
    lastLa = None
    nSats = len(satIds)
    for i, utcTime in enumerate(utcTimes):
        #Extract sub dataframe same time
        subConstDf = constDf[constDf['utcTime'] == utcTime]
        if len(subConstDf) >= nSats:
            if not firstLa:
                firstLa = subConstDf['latitudeArgument'].iloc[0]
                lastLa = subConstDf['latitudeArgument'].iloc[0] - firstLa
            #Brake if done first one orbit
            La = subConstDf['latitudeArgument'].iloc[0] - firstLa if subConstDf['latitudeArgument'].iloc[0] - firstLa >= 0 else subConstDf['latitudeArgument'].iloc[0] - firstLa + 360
            if deltaLa - (La - lastLa) >= 360:
                break
            else:
                deltaLa += (La - lastLa)
                lastLa = La
            #Build image
            ax = subConstDf.plot.scatter(x='rightAscensionAscendingNode', y='latitudeArgument')
            ax.set_xlabel("RAAN [deg]")
            ax.set_ylabel("Latitude Argument [deg]")
            ax.set_title(utcTime)
            ax.set(xlim=[0, 165], ylim=[0, 360])
            figPath = os.path.join(tmpPath, "analysis_constellation-geometry-{}.jpg".format(i))
            images.append(figPath)
            ax.get_figure().savefig(figPath)
            #Save first, image and position
            if i == 0:
                figPath = os.path.join(outputPlotFolderPath, "analysis_constellation-geometry.jpg")
                ax.get_figure().savefig(figPath)
            
    #Save gif
    frames = [Image.open(image) for image in images]
    frame = frames[0]
    frame.save(os.path.join(outputPlotFolderPath, 'analysis_constellation-geometry.gif'), 
                   format="GIF", append_images=frames,
                   save_all=True, duration=100, loop=0)
    #Write
    doc.add_heading("Constellation Geometry", 1)
    doc.add_paragraph('The picture below shows the constellation topology, at simulation time zero: {}'.format(constDf.iloc[0]['utcTime'].replace("T", " at ").replace("Z", "")))
    p = doc.add_paragraph()
    r = p.add_run()
    r.add_picture(figPath)
    
    doc.add_page_break()
    
    print('   - Added section on Constellation Geometry in {:.4f} seconds'.format(time.time() - tick))

# -*- coding: utf-8 -*-