#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

import pandas as pd

from ...utils.filemanager import getBasePath, readInputYmlFile
from jsonschema import validate
import json
import os

""" E2E Performance Simulator pre processor """

NOT_DEFINED = "NOT_DEFINED"

def preProcessSimulationRequest(inputFilePath: str) -> dict:
    """ Read input file and extrac Simulation Request as dictionary """
    #Read file
    simulationRequest = readInputYmlFile(inputFilePath)

    #Validate structure
    simulationRequest = validateSimulationRequest(simulationRequest)

    #Return
    return simulationRequest

################################################################################################

def validateSimulationRequest(simulationRequest: dict) -> dict:
    try:
        #Set validation schema
        simulationRequestSchema = os.path.join('api', 'simulationrequest-schema.json')
        #Validate with schema
        with open(os.path.join(getBasePath(), simulationRequestSchema), "r") as f: 
            validate(instance=simulationRequest, schema=json.load(f))
        return simulationRequest
    
    except Exception as e:
        #Raise error
        raise Exception('ERROR: validation of Simulation Request failed due to: {}'.format(str(e)))

################################################################################################

def readSatellites(simulationRequest: dict) -> list:
    """ Read satellites file and return validated list """
    fileName = simulationRequest['satellites']['file']
    satellitesFilePath = os.path.join(getBasePath(), 'data', 'satellites', fileName)
    satellites = readInputYmlFile(satellitesFilePath)
    #Validate format
    try:
        #Set validation schema
        propagationDataSchema = os.path.join('api', 'satellites-schema.json')
        #Validate with schema
        with open(os.path.join(getBasePath(), propagationDataSchema), "r") as f:
            validate(instance=satellites, schema=json.load(f))
            return satellites['satellites']
    except Exception as e:
        #Raise error
        raise Exception('ERROR: validation of Satellties list from file {} failed due to: {}'.format(satellitesFilePath, str(e)))

def readGroundStations(simulationRequest: dict) -> list:
    """ Read ground stations file and return validated list """
    groundstationsRequest: dict = simulationRequest.get('groundstations', {})
    fileName: str = groundstationsRequest.get('file', NOT_DEFINED)
    if fileName == NOT_DEFINED:
        return []
    groundstationsFilePath = os.path.join(getBasePath(), 'data', 'groundstations', fileName)
    groundstations = readInputYmlFile(groundstationsFilePath)
    #Validate format
    try:
        #Set validation schema
        propagationDataSchema = os.path.join('api', 'groundstations-schema.json')
        #Validate with schema
        with open(os.path.join(getBasePath(), propagationDataSchema), "r") as f:
            validate(instance=groundstations, schema=json.load(f))
            return groundstations['groundstations']
    except Exception as e:
        #Raise error
        raise Exception('ERROR: validation of Ground Stations list from file {} failed due to: {}'.format(groundstationsFilePath, str(e)))

def readUserTerminals(simulationRequest: dict, all: bool = False) -> list:
    """ Read user terminals file and return validated list """
    uts: dict = simulationRequest.get('userterminals', [])
    if uts == []:
        return []
    userTerminals = []
    import random
    for ut in uts:
        fileName = ut['file']
        usage = ut['usage']
        userterminalsFilePath = os.path.join(getBasePath(), 'data', 'userterminals', fileName)
        df = pd.read_csv(userterminalsFilePath, delimiter=r"\s+")
        id = "ut-" + fileName.split("_")[0]
        n = len(df)
        indexes = random.sample(range(n), int(usage * n)) if not all else range(n)
        for i in indexes:
            userTerminals.append({'id' : id + str(int(df.iloc[i]['utIndex'])),
                                'location': {
                                    'latitude': df.iloc[i]['utLat'],
                                    'longitude': df.iloc[i]['utLon'],
                                    'altitude': 0
                                }
                             }
                            )
    # TODO validation
    # #Validate format
    # try:
    #     #Set validation schema
    #     propagationDataSchema = os.path.join('api', 'groundstations-schema.json')
    #     #Validate with schema
    #     with open(os.path.join(getBasePath(), propagationDataSchema), "r") as f:
    #         validate(instance=userterminals, schema=json.load(f))
    #         return userterminals['userterminals']
    # except Exception as e:
    #     #Raise error
    #     raise Exception('ERROR: validation of User Terminals list from file {} failed due to: {}'.format(userterminalsFilePath, str(e)))
    return userTerminals


# -*- coding: utf-8 -*-