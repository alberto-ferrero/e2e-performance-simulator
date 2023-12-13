#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

import os
import time

from ..airlink.request import link
from ..airlink.mapper import getSatelliteAntennaProperties, getUserTerminalAntennaProperties, getGrounStationAntennaProperties

from ..flightdynamics.filemanager import readCsvPropagationDataFiles
from ..airlink.filemanager import saveLinkData, extractLinkDataFromCsv

from ..utils.results import AppResult
from ..utils.timeconverter import getTimestampFromDate
from ..utils.filemanager import saveDictToJson

""" E2E Performance Simulator Air Link Budget Calculator Handler """

def getAirLinkBudgetData(simulationRequest: dict, outputDataFolderPath: str, flightDynamicsDataOutputPath: str) -> str:
    #Check some flight dynamics
    if not flightDynamicsDataOutputPath:
        raise Exception('ERROR: failed due to no Flight Dynamics data provided for Air Link Budget Calculations. Please add Flight Dynamics module to the Simulation Request')

    linkBudgetInfo = simulationRequest['modules']['airlinkBudget']
    
    linkRequestFull = {}

    #Define propagation data source
    if linkBudgetInfo['data'] == 'run':

        print(' - Run Air Link Budget calculation, calling server at {}'.format(linkBudgetInfo['address']))
        tick = time.time()
        
        print('   - Calculate air link budget propagation of {} satellites, {} ground stations, {} user terminals'.format(len(simulationRequest['satellites']), len(simulationRequest['groundstations']), len(simulationRequest['userterminals'])))
        print('   - Calculating air link for contacts from {} to {} ...'.format(simulationRequest['simulationWindow']['start'].replace("T", " at ").replace("Z", ""), simulationRequest['simulationWindow']['end'].replace("T", " at ").replace("Z", "")))
        
        url = linkBudgetInfo['address']

        #Get Air Link Budget request, for each satellite, considering calculated contacts
        linkDataFull = {}
        for sat in simulationRequest['satellites']:
            satId = sat['id']
            #Read propagation data, from Flight Dynamics calculation
            propagationData = readCsvPropagationDataFiles(flightDynamicsDataOutputPath, satId)
            #Get contacts and group by ground stations and user terminals
            contactsData = propagationData['contactList']
            statesData = propagationData['orbitStateList']
            del propagationData
            #Calculate air link budget for groundstations and user terminals
            linkDataFull[satId] = []

            #Check if satellite has Ka connection, to link with user terminal
            if 'Ka' in [ant['band'] for ant in sat['antennas']]:
                for ut in simulationRequest['userterminals']:
                    states = statesData.copy()
                    utId = ut['id']
                    poiContacts = tuple([c for c in contactsData if c['argumentOfInterestId'] == utId])
                    if len(poiContacts) > 0:
                        linkRequest = {}

                        #Build Point of Interest (poi) properties
                        linkRequest['ground'] = {}
                        linkRequest['ground']['id'] = utId
                        linkRequest['ground']['location'] = ut['location']
                        linkRequest['ground']['antenna'] = getUserTerminalAntennaProperties(ut['class'])

                        #Build satellite object with link properties
                        linkRequest['satellite'] = {}
                        linkRequest['satellite']['id'] = satId
                        linkRequest['satellite']['antenna'] = getSatelliteAntennaProperties('Ka')
                
                        #Get states for each contact window
                        satStates = []
                        for c in poiContacts:
                            aos = getTimestampFromDate(c['startUtcTime'])
                            los = getTimestampFromDate(c['endUtcTime'])
                            indexes = [ states.index(s) for s in states if getTimestampFromDate(s['utcTime']) >= aos and getTimestampFromDate(s['utcTime']) <= los]
                            satStates.extend(
                                [
                                    {'utcTime': states[index]['utcTime'],
                                    'X': states[index]['X'],
                                    'Y': states[index]['Y'],
                                    'Z': states[index]['Z']
                                    } 
                                for index in indexes
                                ]
                            )
                            #Remove to speed up
                            indexes.reverse()
                            [states.pop(index) for index in indexes]
                        linkRequest['satellite']['states'] = satStates
                        #Call air link budget calculation and save
                        linkRequestFull[satId] = linkRequest
                        linkDataRes: AppResult = link(url, linkRequest)
                        linkDataFull[satId].extend(linkDataRes.result[satId])
            
            #TODO to add groundstations

        airLinkBudgetDataOutputPath = saveLinkData(outputDataFolderPath, linkDataFull)
        print('   - Air Link Budget calculation completed in {:.4f} seconds'.format(time.time() - tick))
    else:
        print('   - Read Air Link Data from {} repository, at {}'.format(linkBudgetInfo['data'], linkBudgetInfo['address']))
        #Read, validate and return link data
        linkDataRes = extractLinkDataFromCsv(simulationRequest)
        airLinkBudgetDataOutputPath = saveLinkData(outputDataFolderPath, linkDataRes)
    
    saveDictToJson(linkRequestFull, os.path.join(airLinkBudgetDataOutputPath, 'linkrequest.json'))
    
    print('   - Saved Propagation Data in output folder {}'.format(airLinkBudgetDataOutputPath))        
    del linkDataRes, linkRequestFull

    return airLinkBudgetDataOutputPath

# -*- coding: utf-8 -*-