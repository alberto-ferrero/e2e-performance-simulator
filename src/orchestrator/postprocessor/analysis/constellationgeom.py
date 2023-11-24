#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

import os
import glob
import time
import pandas as pd
from math import pi

#Import docx
from docx import Document

""" E2E Performance Simulator Analysis: Constellation Geometry """

def write(doc: Document, outputPlotFolderPath: str, flightDynamicsDataOutputPath: str):
    """Write analyis chapter """
    #Read from Flight Dynamics file and extract mean Keplerian elements
    tick = time.time()
    constDf = pd.DataFrame()
    for fileName in glob.glob(os.path.join(flightDynamicsDataOutputPath, "*_bls-keplerian-state.csv")):
        df = pd.read_csv(fileName)
        df = df[['utcTime', 'rightAscensionAscendingNode', 'argumentPeriapsis', 'meanAnomaly']].iloc[0:1]
        try:
            constDf = pd.concat([constDf, df], axis=0)
        except:
            constDf = df

    if len(constDf) > 0:
        #Build image
        constDf['rightAscensionAscendingNode'] = constDf['rightAscensionAscendingNode'] * 180.0 / pi
        constDf['latitudeArgument'] = (constDf['argumentPeriapsis'] + constDf['meanAnomaly']) * 180.0 / pi
        constDf['latitudeArgument'] = constDf['latitudeArgument'].apply(lambda x: x - 360 if x >= 360 else x)
        ax = constDf.plot.scatter(x='rightAscensionAscendingNode', y='latitudeArgument')
        ax.set_xlabel("RAAN [deg]")
        ax.set_ylabel("Latitude Argument [deg]")
        figPath = os.path.join(outputPlotFolderPath, "analysis_constellation-geometry.png")
        ax.get_figure().savefig(figPath)

        #Write       
        doc.add_heading("Constellation Geometry", 1)
        doc.add_paragraph('The picture below shows the constellation topology, at simulation time zero: {}'.format(constDf.iloc[0]['utcTime'].replace("T", " at ").replace("Z", "")))
        p = doc.add_paragraph()
        r = p.add_run()
        r.add_picture(figPath)
        
        doc.add_page_break()

        print(' - Added section on Constellation Geometry in  {:.4f} seconds'.format(time.time() - tick))

# -*- coding: utf-8 -*-