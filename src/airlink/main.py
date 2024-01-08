#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

import os
import time

from ..airlink.request import airlink, getAirLinkRequest

from ..orchestrator.preprocessor.preprocessor import readSatellites, readGroundStations, readUserTerminals
from ..flightdynamics.filemanager import readCsvPropagationDataFilesAsDataframe
from ..airlink.filemanager import saveAirLinkData, extractAirLinkDataFromCsv
from ..airlink.mapper import Band, getGrounStationAntennaProperties, getUserTerminalAntennaProperties, getSatelliteAntennaProperties

from ..utils.results import AppResult
from ..utils.timeconverter import getTimestampFromDate
from ..utils.filemanager import saveDictToJson

""" E2E Performance Simulator Air Link Budget Calculator Handler """

def getAirLinkBudgetData(simulationRequest: dict, outputDataFolderPath: str, flightDynamicsDataOutputPath: str) -> str:
    #Check some flight dynamics
    if not flightDynamicsDataOutputPath:
        raise Exception('ERROR: failed due to no Flight Dynamics data provided for Air Link Budget Calculations. Please add Flight Dynamics module to the Simulation Request')

    linkBudgetInfo = simulationRequest['modules']['airLinkBudget']
    
    linkRequestFull = {}

    #Define propagation data source
    if linkBudgetInfo['data'] == 'run':

        print(' - Run Air Link Budget calculation, calling server at {}'.format(linkBudgetInfo['address']))
        tick = time.time()
        
        print('   - Calculate air link budget propagation of {} satellites, {} ground stations, {} user terminals'.format(len(simulationRequest['satellites']), len(simulationRequest['groundstations']), len(simulationRequest['userterminals'])))
        print('   - Calculating air link for contacts from {} to {} ...'.format(simulationRequest['simulationWindow']['start'].replace("T", " at ").replace("Z", ""), simulationRequest['simulationWindow']['end'].replace("T", " at ").replace("Z", "")))
        
        url = linkBudgetInfo['address']

        #Load assets
        satellites = readSatellites(simulationRequest)
        groundstations = readGroundStations(simulationRequest)
        userterminals = readUserTerminals(simulationRequest)

        #Read propagation data, from Flight Dynamics calculation
        propagationDataFrame = readCsvPropagationDataFilesAsDataframe(flightDynamicsDataOutputPath)

        #Get Air Link Budget request, for each satellite, considering calculated contacts
        
        for sat in satellites:
            satId = sat['id']
            #Get contacts and group by ground stations and user terminals
            contactsDf = propagationDataFrame[satId]['contactList']
            statesDf = propagationDataFrame[satId]['orbitStateList']
            statesDf['timestamp'] = statesDf['utcTime'].apply(getTimestampFromDate)

            #Calculate air link budget for groundstations and user terminals
            airLinkData = []

            #Check if satellite has Ka connection, to link with user terminal
            if 'Ka' in [ant['band'] for ant in sat['antennas']]:
                satelliteAntennaProperties = getSatelliteAntennaProperties(Band.Ka)
                for ut in userterminals:
                    groundAntennaProperties = getUserTerminalAntennaProperties(ut['class'])
                    airLinkRequest = getAirLinkRequest(satId, satelliteAntennaProperties, statesDf, contactsDf, ut['id'], ut['location'], groundAntennaProperties)
                    #Call air link budget calculation and save
                    if airLinkRequest != {}:
                        linkRequestFull[satId] = airLinkRequest
                        airLinkDataRes: AppResult = airlink(url, airLinkRequest)
                        airLinkData.extend(airLinkDataRes.result[satId])

            #Check if satellite has S connection, to link with user terminal
            if 'S' in [ant['band'] for ant in sat['antennas']]:
                satelliteAntennaProperties = getSatelliteAntennaProperties(Band.S)
                groundAntennaProperties = getGrounStationAntennaProperties(Band.S)
                for gs in groundstations:
                    airLinkRequest = getAirLinkRequest(satId, satelliteAntennaProperties, statesDf, contactsDf, gs['id'], gs['location'], groundAntennaProperties)
                    #Call air link budget calculation and save
                    if airLinkRequest != {}:
                        linkRequestFull[satId] = airLinkRequest
                        airLinkDataRes: AppResult = airlink(url, airLinkRequest)
                        airLinkData.extend(airLinkDataRes.result[satId])

            #Save for satId
            airLinkBudgetDataOutputPath = saveAirLinkData(outputDataFolderPath, airLinkData)
            
        print('   - Air Link Budget calculation completed in {:.4f} seconds'.format(time.time() - tick))
    
    else:
        print('   - Read Air Link Data from {} repository, at {}'.format(linkBudgetInfo['data'], linkBudgetInfo['address']))
        #Read, validate and return link data
        airLinkDataRes = extractAirLinkDataFromCsv(simulationRequest)
        for satId in airLinkDataRes:
            airLinkBudgetDataOutputPath = saveAirLinkData(outputDataFolderPath, satId, airLinkDataRes[satId])
    
    saveDictToJson(linkRequestFull, os.path.join(airLinkBudgetDataOutputPath, 'linkrequest.json'))
    
    print('   - Saved Propagation Data in output folder {}'.format(airLinkBudgetDataOutputPath))        
    return airLinkBudgetDataOutputPath

# -*- coding: utf-8 -*-