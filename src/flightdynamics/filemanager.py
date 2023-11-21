#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

import os

from ..utils.filemanager import makeOutputFolder, saveListDictToCsv, readLocalCsvToDict, readRemoteCsvToDict, getBasePath
from jsonschema import validate
import json

#Define Propagation Data csv file tag
PROPAGATION_DATA_FILES_MAP = {
    "orbitStateList": "orbit-state",
    "keplerianStateList": "keplerian-state",
    "blsKeplerianStateList": "bls-keplerian-state",
    "contactList": "contacts",
    "tles": "tles"
}

""" E2E Performance Simulator Flight Dynamics Provider Handler File Manager """

def readCsvPropagationDataFiles(simulationRequest: dict, satId: str) -> list:
    """ Read csv propagation state file and validate """
    propagationData = {}
    for propagationDataEntry, propgationDataFile in PROPAGATION_DATA_FILES_MAP.items():
        #Build file name as convention /path/satId-stateTag.csv
        filePath = os.path.join(simulationRequest['flightDynamics']['address'], satId + "_" + propgationDataFile + ".csv")
        #Read from file
        if simulationRequest['flightDynamics']['data'] == 'local':
            orbitData = readLocalCsvToDict(filePath)
        else:
            orbitData = readRemoteCsvToDict(filePath)
        propagationData[propagationDataEntry] = orbitData

    #Validate
    try:
        #Set validation schema
        propagationDataSchema = os.path.join('api', 'propagationdata-schema.json')
        #Validate with schema
        with open(os.path.join(getBasePath(), propagationDataSchema), "r") as f:
            validate(instance=propagationData, schema=json.load(f))
        return propagationData
    except Exception as e:
        #Raise error
        raise Exception('ERROR: validation of Propagation Data for satellite {} failed due to: {}'.format(satId, str(e)))
    
def savePropagationData(outputDataFolderPath: str, propagationData: dict):
    """ Save to output/data/flightdynamics """
    outputPath = os.path.join(outputDataFolderPath, 'flightdyanmics')
    makeOutputFolder(outputPath)
    for satId in propagationData:
        for propagationDataEntry, propgationDataFile in PROPAGATION_DATA_FILES_MAP.items():
            saveListDictToCsv(propagationData[satId][propagationDataEntry], os.path.join(outputPath, satId + "_" + propgationDataFile + ".csv"))

# -*- coding: utf-8 -*-