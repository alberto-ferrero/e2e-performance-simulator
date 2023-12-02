#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

import os
import glob
import time

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as md

from ....utils.filemanager import makeOutputFolder
from ....utils.timeconverter import getDatetimeFromDate

# Register time converters
pd.plotting.register_matplotlib_converters()

#Import docx
from docx import Document

""" E2E Performance Simulator Analysis: Contacts """

def write(doc: Document, outputDataFolderPath: str, outputPlotFolderPath: str, flightDynamicsDataOutputPath: str):
    """Write analyis chapter """
    tick = time.time()
    #Read from Flight Dynamics file and extract contacts info
    utsDf = {}
    gssDf = {}
    for fileName in glob.glob(os.path.join(flightDynamicsDataOutputPath, "*_contacts.csv")):
        satId = fileName.split(os.sep)[-1].split("_")[0]
        df = pd.read_csv(fileName)
        df = df[['argumentOfInterestId', 'startUtcTime', 'endUtcTime']]
        df['satId'] = satId
        # Store contacts for the args
        argIds = set(df['argumentOfInterestId'].to_list())
        for argId in argIds:
            filteredDf = df.copy()
            filteredDf = filteredDf[filteredDf['argumentOfInterestId'] == argId]
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
    doc.add_heading("Propagated Contacts", 1)

    ###################################################################
    #Plot number of visible satellites for each User Terminal and Ground Station
    xfmt = md.DateFormatter('%Y-%m-%d %H')
    for t, d, descr in (("GS", gssDf, 'ground stations'), ("UT", utsDf, 'user terminals')):
        
        ###################################################################
        #Set up figure
        fig, ax = plt.subplots(len(d), sharex=True, figsize=(7, 7))
        plt.subplots_adjust(hspace=.02)
        fig.suptitle("Satellite Visibility for {}s".format(t))
        #Set to list if only 1 subplot
        if len(d) == 1:
            ax = (ax,)
        
        maxContacts: list = []
        dates: list = []
        fileName = 'analysis-' + t + '-sat-visibility'
        for idx, (poiId, df) in enumerate(d.items()):
            
            ###############################################################
            #Extract number of contacts
            startTimeDf: pd.DataFrame = df[['startUtcTime']].copy()
            startTimeDf.rename(columns={"startUtcTime": "time"}, inplace=True)
            startTimeDf['contact'] = 1
            endTimeDf: pd.DataFrame = df[['endUtcTime']].copy()
            endTimeDf.rename(columns={"endUtcTime": "time"}, inplace=True)
            endTimeDf['contact'] = -1
            contactTimeDf = pd.concat([startTimeDf, endTimeDf], ignore_index=True)
            contactTimeDf['time'] = contactTimeDf['time'].apply(getDatetimeFromDate)
            contactTimeDf.sort_values(by='time', inplace=True)
            pd.to_datetime(contactTimeDf['time'], format='%Y-%m-%dT%H:%M:%S.%fZ')
            dates.extend([contactTimeDf['time'].to_list()[0], contactTimeDf['time'].to_list()[-1]])
            contactTimeDf['contacts'] = contactTimeDf['contact'].cumsum()
            maxContacts.append(max(contactTimeDf['contacts'].to_list()))
            #Plot
            ax[idx].plot(contactTimeDf['time'], contactTimeDf['contacts'], drawstyle="steps-post",  linewidth=0.3)

        #Resize and set tags
        maxContacts = max(maxContacts)
        yTicks = np.arange(0, maxContacts + 1, 2).tolist()
        minDate = min(dates)
        maxDate = max(dates)
        for idx, id in enumerate(d.keys()):
            ax[idx].text(0.97, 0.5, id, horizontalalignment='left', verticalalignment='center', transform=ax[idx].transAxes)
            ax[idx].xaxis.set_major_formatter(xfmt)
            ax[idx].set_xlim([minDate, maxDate])
            ax[idx].tick_params(axis='x', rotation=90)
            ax[idx].set_ylim([0, maxContacts])
            ax[idx].set_yticks(yTicks)

        #Save
        figPath = os.path.join(outputPlotFolderPath, fileName + '.png')
        fig.savefig(figPath, bbox_inches='tight')
        
        doc.add_paragraph('The picture below shows {} contacts, depicting the number of satellites in visibility'.format(descr))
        p = doc.add_paragraph()
        r = p.add_run()
        r.add_picture(figPath)

    plt.close('all')
    print('   - Added section on Ground Stations and User Terminals Contacts in {:.4f} seconds'.format(time.time() - tick))


# -*- coding: utf-8 -*-