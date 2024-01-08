#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

import os
from jsonschema import validate
import json
import time

from ..utils.results import AppResult
from ..flightdynamics.filemanager import readCsvPropagationDataFiles, savePropagationData
from ..orchestrator.preprocessor.preprocessor import readSatellites, readUserTerminals, readGroundStations
from ..utils.filemanager import getBasePath, saveDictToJson
from ..utils.timeconverter import getTimestampFromDate
from .request import propagate

DEFAULT_PERIODIC_UPDATE = 1000000 #[sec]

""" E2E Performance Simulator Flight Dynamics Provider Handler """

def getFlightDynamicsPropagationData(simulationRequest: dict, outputDataFolderPath: str) -> str:
    flightDynamicsInfo = simulationRequest['modules']['flightDynamics']
    propagationRequest = {}

    #Define propagation data source
    if flightDynamicsInfo['data'] == 'run':

        #Constants
        N_MAX_SATS = 20

        def getAssetById(assets: list, id: str) -> dict:
            for asset in assets:
                if asset['id'] == id:
                    return asset.copy()
            return Exception("ERROR: in list of assets, not possible to find one with id {}".format(id))
        
        def getSubSetPropagationRequest(propagationRequest: dict, idxi: int, idf: int) -> dict:
            #Get batch of assets
            subPropagationRequest = {}
            subPropagationRequest['scenario'] = propagationRequest['scenario']
            subPropagationRequest['assets'] = propagationRequest['assets'][idxi:idf+1]
            subPropagationRequest['pointsOfInterest'] = propagationRequest['pointsOfInterest']
            #Extend with non propagating satellties for ISV
            satIds = [sat['id'] for sat in subPropagationRequest['assets']]
            soiIds = []
            for sat in subPropagationRequest['assets']:
                spaceContacts = sat['spaceContacts']
                for soiId in spaceContacts:
                    if soiId not in soiIds and soiId not in satIds:
                        soiIds.append(soiId)
                        soi = getAssetById(propagationRequest['assets'], soiId)
                        soi['propagate'] = False
                        subPropagationRequest['assets'].append(soi)
            return subPropagationRequest

        print(' - Run Flight Dynamics propagation, calling server at {}'.format(flightDynamicsInfo['address']))
        tick = time.time()
        
        #Get proagation request
        propagationRequest: dict = extractFlightDynamicsScenario(simulationRequest)
        groundText = 'capturing ground contacts, ' if simulationRequest['satellites']['groundcontacts'] else 'no ground contacts, '
        spaceText = 'capturing ground contacts between stellites' if simulationRequest['satellites']['spacecontacts'] else 'no space contacts'
        print('   - Launch propagation of {} satellites, '.format(len(propagationRequest['assets'])) + groundText + spaceText)
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
        "periodicUpdate": simulationRequest['modules']['flightDynamics']['properties'].get('periodicUpdate', DEFAULT_PERIODIC_UPDATE),
        "propagator": {
            "type": simulationRequest['modules']['flightDynamics']['properties']['propagator']
        }
    }

    #Build points of interest, if capture ground contacts
    propagationRequest['pointsOfInterest'] = []
    if simulationRequest['satellites'].get('groundcontacts', False):
        userterminals = readUserTerminals(simulationRequest)
        groundstations = readGroundStations(simulationRequest)
        propagationRequest['pointsOfInterest'] = [
            {
                'id': poi['id'],
                'altitude': poi['location']['altitude'],
                'latitude': poi['location']['latitude'],
                'longitude': poi['location']['longitude']
            }
        for poi in  userterminals + groundstations
        ]
    poiIds = [poi['id'] for poi in propagationRequest['pointsOfInterest']]
    
    #Build satellites, considering default properties
    satellites = readSatellites(simulationRequest)
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
      for sat in satellites
    ]
    satIds = [sat['id'] for sat in propagationRequest['assets']]

    #Validate contacts
    for sat in propagationRequest['assets']:
        if simulationRequest['satellites'].get('groundcontacts', False):
            for groundContactId in sat['groundContacts']:
                if groundContactId not in poiIds:
                    raise Exception("ERROR: for satellite {}, contact with ground point {} not possible as ground point not defined as ground station nor user terminal".format(sat['id'], groundContactId))
        else:
            sat['groundContacts'] = []
        if simulationRequest['satellites'].get('spacecontacts', False):
            for spaceContactId in sat['spaceContacts']:
                if spaceContactId not in satIds:
                    raise Exception("ERROR: for satellite {}, contact with satellite {} not possible as ground point not defined as ground station nor user terminal".format(sat['id'], spaceContactId))
        else:
            sat['spaceContacts'] = []

    # TODO to add area of interest and angles crossing
    return propagationRequest

def extractPropagationDataFromCsv(simulationRequest: dict) -> dict:
    """ Read from repository required csv files and parse back to propagation data """
    #Build Propagation Data object reading from stored files
    flightDynamicsDataPath = simulationRequest['modules']['flightDynamics']['address']
    source = simulationRequest['modules']['flightDynamics']['data']
    propagationData: dict = {}
    propagationData = readCsvPropagationDataFiles(flightDynamicsDataPath, source)
    #Validate format
    try:
        #Set validation schema
        propagationDataSchema = os.path.join('api', 'propagationdata-schema.json')
        #Validate with schema
        with open(os.path.join(getBasePath(), propagationDataSchema), "r") as f:
            validate(instance=propagationData, schema=json.load(f))
    except Exception as e:
        #Raise error
        raise Exception('ERROR: validation of Propagation Data failed due to: {}'.format(str(e)))

    return AppResult(200, {"local": simulationRequest['modules']['flightDynamics']['address']}, propagationData)

# -*- coding: utf-8 -*-