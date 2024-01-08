#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

import os
import time

from ..spacelink.request import spacelink, getSpaceLinkRequest

from ..orchestrator.preprocessor.preprocessor import readSatellites
from ..flightdynamics.filemanager import readCsvPropagationDataFilesAsDataframe
from ..spacelink.filemanager import extractSpaceLinkDataFromCsv, saveSpaceLinkData

from ..utils.results import AppResult
from ..utils.timeconverter import getTimestampFromDate
from ..utils.filemanager import saveDictToJson

""" E2E Performance Simulator Space Link Budget Handler """

def getSpaceLinkBudgetData(simulationRequest: dict, outputDataFolderPath: str, flightDynamicsDataOutputPath: str) -> str:
    #Check some flight dynamics
    if not flightDynamicsDataOutputPath:
        raise Exception('ERROR: failed due to no Flight Dynamics data provided for Space Link Budget Calculations. Please add Flight Dynamics module to the Simulation Request')

    linkBudgetInfo = simulationRequest['modules']['spaceLinkBudget']
    
    linkRequestFull = {}

    #Define propagation data source
    if linkBudgetInfo['data'] == 'run':

        print(' - Run Space Link Budget calculation, calling server at {}'.format(linkBudgetInfo['address']))
        tick = time.time()
        
        print('   - Calculate space link budget propagation of {} satellites, {} ground stations, {} user terminals'.format(len(simulationRequest['satellites']), len(simulationRequest['groundstations']), len(simulationRequest['userterminals'])))
        print('   - Calculating space link for contacts from {} to {} ...'.format(simulationRequest['simulationWindow']['start'].replace("T", " at ").replace("Z", ""), simulationRequest['simulationWindow']['end'].replace("T", " at ").replace("Z", "")))
        
        url = linkBudgetInfo['address']

        #Load assets
        satellites = readSatellites(simulationRequest)
     
        #Read propagation data, from Flight Dynamics calculation
        propagationData = readCsvPropagationDataFilesAsDataframe(flightDynamicsDataOutputPath)

        #Pre process dataframes, adding timestamps and filtering only Inter Satellite Visibility (ISV)
        satIds = [sat['id'] for sat in satellites]
        satStatesDf = {}
        satContactsDf = {}
        for satId in satIds:
            statesDf = propagationData[satId]['orbitStateList']
            statesDf['timestamp'] = statesDf['utcTime'].apply(getTimestampFromDate)
            contactsDf = propagationData[satId]['contactList']
            contactsDf = contactsDf[contactsDf['contactType'] == 'ISV']
            contactsDf['startTimestamp'] = contactsDf['startUtcTime'].apply(getTimestampFromDate)
            contactsDf['endTimestamp'] = contactsDf['endUtcTime'].apply(getTimestampFromDate)
            #Store
            satStatesDf[satId] = statesDf
            satContactsDf[satId] = contactsDf
        
        del propagationData

        #Get Space Link Budget request, for each satellite, considering calculated contacts        
        for satId in satIds:
            #Calculate space link
            spaceLinkRequest = getSpaceLinkRequest(satId, satStatesDf, satContactsDf[satId])
            linkRequestFull[satId] = spaceLinkRequest
            spaceLinkDataRes: AppResult = spacelink(url, spaceLinkRequest)
            #Save for satId
            spaceLinkBudgetDataOutputPath = saveSpaceLinkData(outputDataFolderPath, satId, spaceLinkDataRes.result[satId])
            
        print('   - Space Link Budget calculation completed in {:.4f} seconds'.format(time.time() - tick))
    
    else:
        print('   - Read Space Link Data from {} repository, at {}'.format(linkBudgetInfo['data'], linkBudgetInfo['address']))
        #Read, validate and return link data
        spaceLinkDataRes = extractSpaceLinkDataFromCsv(simulationRequest)
        for satId in spaceLinkDataRes:
            spaceLinkBudgetDataOutputPath = saveSpaceLinkData(outputDataFolderPath, satId, spaceLinkDataRes[satId])
    
    saveDictToJson(linkRequestFull, os.path.join(spaceLinkBudgetDataOutputPath, 'linkrequest.json'))
    
    print('   - Saved Propagation Data in output folder {}'.format(spaceLinkBudgetDataOutputPath))        
    return spaceLinkBudgetDataOutputPath

# -*- coding: utf-8 -*-