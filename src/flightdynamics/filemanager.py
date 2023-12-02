#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

import os

from ..utils.results import AppResult
from ..utils.filemanager import makeOutputFolder, saveListDictToCsv, readLocalCsvToDict, readRemoteCsvToDict

#Define Propagation Data csv file tag
PROPAGATION_DATA_FILES_MAP = {
    "orbitStateList": "orbit-state",
    "keplerianStateList": "keplerian-state",
    "blsKeplerianStateList": "bls-keplerian-state",
    "contactList": "contacts",
    "tles": "tles"
}

""" E2E Performance Simulator Flight Dynamics Provider Handler File Manager """

def readCsvPropagationDataFiles(flightDynamicsDataPath: str, satId: str, source: str = 'local') -> list:
    """ Read csv propagation data files and validate
        source 'local' from local repository, source 'remote' from remote git repository 
    """
    propagationData = {}
    for propagationDataEntry, propgationDataFile in PROPAGATION_DATA_FILES_MAP.items():
        #Build file name as convention /path/satId-stateTag.csv
        filePath = os.path.join(flightDynamicsDataPath, satId + "_" + propgationDataFile + ".csv")
        #Read from file
        if source == 'local':
            orbitDataParsed = readLocalCsvToDict(filePath)
        else:
            orbitDataParsed = readRemoteCsvToDict(filePath)
        propagationData[propagationDataEntry] = orbitDataParsed
    return propagationData

def savePropagationData(outputDataFolderPath: str, propagationData: AppResult):
    """ Save to output/data/flightdynamics """
    outputPath = os.path.join(outputDataFolderPath, 'flightdynamics')
    makeOutputFolder(outputPath)
    result = propagationData.result
    for satId in result:
        for propagationDataEntry, propgationDataFile in PROPAGATION_DATA_FILES_MAP.items():
            if propagationDataEntry not in result[satId]:
                result[satId][propagationDataEntry] = []
            saveListDictToCsv(result[satId][propagationDataEntry], os.path.join(outputPath, satId + "_" + propgationDataFile + ".csv"))
    return outputPath

# -*- coding: utf-8 -*-