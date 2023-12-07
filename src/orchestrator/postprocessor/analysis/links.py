#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

import os
import glob
import time

import pandas as pd
import matplotlib.pyplot as plt

from ....utils.filemanager import makeOutputFolder

# Register time converters
pd.plotting.register_matplotlib_converters()

#Import docx
from docx import Document

""" E2E Performance Simulator Analysis: Links """

def write(doc: Document, outputDataFolderPath: str, outputPlotFolderPath: str, linkDataOutputPath: str):
    """Write analyis chapter """
    tick = time.time()
    #Read from Link Budget file and extract links info
    utsDf = {}
    gssDf = {}
    for fileName in glob.glob(os.path.join(linkDataOutputPath, "*_Link-Data.csv")):
        satId = fileName.split(os.sep)[-1].split("_")[0]
        df = pd.read_csv(fileName)
        df = df[['grId', 'utcTime', 'uCNR', 'dCNR']]
        df['satId'] = satId
        # Store links for the args
        argIds = set(df['grId'].to_list())
        for argId in argIds:
            filteredDf = df.copy()
            filteredDf = filteredDf[filteredDf['grId'] == argId]
            if 'ut-' in argId:
                if argId not in utsDf:
                    utsDf[argId] = filteredDf
                else:
                    utsDf[argId] = pd.concat([utsDf[argId], filteredDf], ignore_index=True)
                utsDf[argId].index
            if 'gs-' in argId:
                if argId not in gssDf:
                    gssDf[argId] = filteredDf
                else:
                    gssDf[argId] = pd.concat([gssDf[argId], filteredDf], ignore_index=True)
                gssDf[argId].index

    if gssDf == {} and utsDf == {}:
        return

    outputAnalysFolderPath = os.path.join(outputDataFolderPath, 'analysis')
    makeOutputFolder(outputAnalysFolderPath)
    
    #Write       
    doc.add_heading("Calculated Links", 1)

    ###################################################################
    #Plot number of visible satellites for each User Terminal and Ground Station
    #TODO

    plt.close('all')
    print('   - Added section on Ground Stations and User Terminals Link analysis in {:.4f} seconds'.format(time.time() - tick))


# -*- coding: utf-8 -*-