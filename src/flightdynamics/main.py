#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

import os
from jsonschema import validate
import json
import time

from ..utils.results import AppResult
from ..flightdynamics.filemanager import readCsvPropagationDataFiles, savePropagationData
from ..utils.filemanager import getBasePath, saveDictToJson
from ..utils.timeconverter import getTimestampFromDate
from .request import propagate

""" E2E Performance Simulator Flight Dynamics Provider Handler """

def getFlightDynamicsPropagationData(simulationRequest: dict, outputDataFolderPath: str) -> str:
    
    flightDynamicsInfo = simulationRequest['modules']['flightDynamics']
    propagationRequest = {}

    #Define propagation data source
    if flightDynamicsInfo['data'] == 'run':

        #Constants
        N_MAX_SATS = 20
        
        def getSubSetPropagationRequest(propagationRequest: dict, idxi: int, idf: int) -> dict:
            #Get batch of assets
            subPropagationRequest = {}
            subPropagationRequest['scenario'] = propagationRequest['scenario']
            subPropagationRequest['assets'] = propagationRequest['assets'][idxi:idf+1]
            subPropagationRequest['pointsOfInterest'] = propagationRequest['pointsOfInterest']
            return subPropagationRequest

        print(' - Run Flight Dynamics propagation, calling server at {}'.format(flightDynamicsInfo['address']))
        tick = time.time()
        
        #Get proagation request
        propagationRequest: dict = extractFlightDynamicsScenario(simulationRequest)
        print('   - Launch propagation of {} satellites, {} ground stations, {} user terminals'.format(len(simulationRequest['satellites']), len(simulationRequest['groundstations']), len(simulationRequest['userterminals'])))
        print('   - Propagating orbit from {} to {} ...'.format(simulationRequest['simulationWindow']['start'].replace("T", " at ").replace("Z", ""), simulationRequest['simulationWindow']['end'].replace("T", " at ").replace("Z", "")))
        
        url = flightDynamicsInfo['address']

        #Propagate and return propagation data, cutting run to not overkill memory
        nSats = len(propagationRequest['assets'])

        for ii in range(int(nSats / N_MAX_SATS)):
            #Get batch of assets, call app and get results
            subPropagationRequest = getSubSetPropagationRequest(propagationRequest, ii * N_MAX_SATS, ((ii + 1) * N_MAX_SATS) - 1)
            propagationDataRes: AppResult = propagate(url, subPropagationRequest)
            flightDynamicsDataOutputPath = savePropagationData(outputDataFolderPath, propagationDataRes)

        if nSats % N_MAX_SATS != 0:
            # Get batch of assets, call app and get results
            subPropagationRequest = getSubSetPropagationRequest(propagationRequest, int(nSats / N_MAX_SATS) * N_MAX_SATS, int(nSats / N_MAX_SATS) * N_MAX_SATS + nSats % N_MAX_SATS)
            propagationDataRes: AppResult = propagate(url, subPropagationRequest)
            flightDynamicsDataOutputPath = savePropagationData(outputDataFolderPath, propagationDataRes)
        
        print('   - Propagation completed in {:.4f} seconds'.format(time.time() - tick))
    
    else:
        print('   - Read Propagation Data from {} repository, at {}'.format(flightDynamicsInfo['data'], flightDynamicsInfo['address']))
        #Read, validate and return propagation data
        propagationDataRes = extractPropagationDataFromCsv(simulationRequest)
        flightDynamicsDataOutputPath = savePropagationData(outputDataFolderPath, propagationDataRes)
    saveDictToJson(propagationRequest, os.path.join(flightDynamicsDataOutputPath, 'propagationrequest.json'))
    
    print('   - Saved Propagation Data in output folder {}'.format(flightDynamicsDataOutputPath))        
    del propagationDataRes

    return flightDynamicsDataOutputPath


#######################################################################################################

def extractFlightDynamicsScenario(simulationRequest: dict) -> dict:
    """ From Simulation Request, extract information to build Flight Dynamics Propagation Request """

    def mapSatelliteOrbit(orbitObj: dict) -> dict:
        if orbitObj['type'] == "TLE":
            return orbitObj
        else:
            #Replace time from UTC time to UTC Epoch millis
            orbitObj['utcEpochMillis'] = getTimestampFromDate(orbitObj['utcTime'])
            orbitObj.pop('utcTime', None)
            return orbitObj

    from ..flightdynamics import satellite as rsnsat

    propagationRequest = {}

    #Build scenario info
    propagationRequest['scenario'] = {
        'id': 'fd-' + simulationRequest['id'],
        "startTimestamp": getTimestampFromDate(simulationRequest['simulationWindow']['start']),
        "endTimestamp": getTimestampFromDate(simulationRequest['simulationWindow']['end']),
        "periodicUpdate": simulationRequest['modules']['flightDynamics']['properties']['periodicUpdate'],
        "propagator": {
            "type": simulationRequest['modules']['flightDynamics']['properties']['propagator']
        }
    }

    #Build satellites, considering default properties
    propagationRequest['assets'] = propagationRequest['assets'] = [
        {
            'id': sat['id'],
            'archetype': 'satellite',
            'orbit': mapSatelliteOrbit(sat['orbit']),
            'mass': sat.get('mass', rsnsat.mass),
            'reflectionCoefficient': sat.get('reflectionCoefficient', rsnsat.Cr),
            'dragCoefficient': sat.get('dragCoefficient', rsnsat.Cd),
            'geometry': sat.get('geometry', rsnsat.getGeometry()),
            'solarArrays': sat.get('solarArrays', rsnsat.getSolarArrays()),
            'thrusters': sat.get('thrusters', rsnsat.getPropulsionSystem()),
            'groundContacts': sat.get('groundContacts', []),
            'spaceContacts': sat.get('spaceContacts', [])
        }
      for sat in simulationRequest.get('satellites', [])
    ]

    #Build points of interest
    propagationRequest['pointsOfInterest'] = [
        {
            'id': poi['id'],
            'altitude': poi['location']['altitude'],
            'latitude': poi['location']['latitude'],
            'longitude': poi['location']['longitude']
        }
      for poi in simulationRequest.get('groundstations', []) + simulationRequest.get('userterminals', [])
    ]

    # TODO to add area of interest and angles crossing

    return propagationRequest

def extractPropagationDataFromCsv(simulationRequest: dict) -> dict:
    """ Read from repository required csv files and parse back to propagation data """
     
    def validateStateTime(orbitData: list, startTimestamp: int, endTimestamp: int, satId: str, stateTag: str):
        if getTimestampFromDate(orbitData[0]['utcTime']) != startTimestamp:
            raise Exception('ERROR: incopatible start propagation time {} in file containing {} for satellite {}'.format(orbitData[0]['utcTime'], stateTag, satId))
        if getTimestampFromDate(orbitData[-1]['utcTime']) != endTimestamp:
            raise Exception('ERROR: incopatible end propagation time {} in file containing {} for satellite {}'.format(orbitData[-1]['utcTime'], stateTag, satId))
    
    def validateContacts(contactsData: list, startTimestamp: int, endTimestamp: int, satId: str, argOfInterestIds: list, stateTag: str):
        if contactsData:
            for contact in contactsData:
                #Check time
                if 'utcTime' in contact and getTimestampFromDate(contact['utcTime']) < startTimestamp:
                    raise Exception('ERROR: incopatible contact as prior start propagation time {} in file containing {} for satellite {}'.format(contact['utcTime'], stateTag, satId))
                elif 'startUtcTime' in contact and getTimestampFromDate(contact['startUtcTime']) < startTimestamp:
                    raise Exception('ERROR: incopatible contact as prior start propagation time {} in file containing {} for satellite {}'.format(contact['startUtcTime'], stateTag, satId))
                if 'utcTime' in contact and getTimestampFromDate(contact['utcTime']) > endTimestamp:
                    raise Exception('ERROR: incopatible contact as after end propagation time {} in file containing {} for satellite {}'.format(contact['utcTime'], stateTag, satId))
                elif 'endUtcTime' in contact and getTimestampFromDate(contact['startUtcTime']) > endTimestamp:
                    raise Exception('ERROR: incopatible contact as after end propagation time {} in file containing {} for satellite {}'.format(contact['endUtcTime'], stateTag, satId))
                #Compatible argument of interest
                if contact['argumentOfInterestId'] not in argOfInterestIds:
                    raise Exception('ERROR: incopatible contact as not supported argument of interest id {} in file containing {} for satellite {}'.format(contact['argumentOfInterestId'], stateTag, satId))

    def validateSatelliteIds(propagationData: dict, satIds: list):
        propSatIds = set([satId for satId in propagationData])
        if propSatIds != set(satIds):
            raise Exception('ERROR: requested satellites from Simulation Request ({}) are not matching the propagated data from files ({})'.format(set(satIds), propSatIds))

    #Get simulation time
    startTimestamp = getTimestampFromDate(simulationRequest['simulationWindow']['start'])
    endTimestamp = getTimestampFromDate(simulationRequest['simulationWindow']['end'])

    #Get list of assets
    satIds = [sat['id'] for sat in simulationRequest['satellites']]
    
    #Build Propagation Data object reading from stored files
    flightDynamicsDataPath = simulationRequest['modules']['flightDynamics']['address']
    source = simulationRequest['modules']['flightDynamics']['data']
    propagationData: dict = {}
    for satellite in simulationRequest['satellites']:
        satId = satellite['id']
        propagationData[satId]: dict = {}
        propagationData[satId] = readCsvPropagationDataFiles(flightDynamicsDataPath, satId, source)

        #Validate content
        for orbitDataTag, orbitData in propagationData[satId].items():
            if 'State' in orbitDataTag:
                validateStateTime(orbitData, startTimestamp, endTimestamp, satId, orbitDataTag)
            if 'contact' in orbitDataTag:
                #Get arguments of interest for satellite
                groundContacts = satellite.get('groundContacts', [])
                spaceContacts = satellite.get('spaceContacts', [])
                validateContacts(orbitData, startTimestamp, endTimestamp, satId, set(groundContacts + spaceContacts), orbitDataTag)
            
    #Validate satellites
    validateSatelliteIds(propagationData, satIds)

    #Validate format
    try:
        #Set validation schema
        propagationDataSchema = os.path.join('api', 'propagationdata-schema.json')
        #Validate with schema
        with open(os.path.join(getBasePath(), propagationDataSchema), "r") as f:
            validate(instance=propagationData, schema=json.load(f))
    except Exception as e:
        #Raise error
        raise Exception('ERROR: validation of Propagation Data for satellite {} failed due to: {}'.format(satId, str(e)))

    return AppResult(200, {"local": simulationRequest['modules']['flightDynamics']['address']}, propagationData)

# -*- coding: utf-8 -*-