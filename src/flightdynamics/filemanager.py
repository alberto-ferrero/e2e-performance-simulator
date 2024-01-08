#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

import os
import pandas as pd

from ..utils.results import AppResult
from ..utils.filemanager import makeOutputFolder, saveListDictToCsv
from ..utils.filemanager import readLocalCsvToDict, readRemoteCsvToDict, readRemoteCsvToDf, readLocalCsvToDf

#Define Propagation Data csv file tag
PROPAGATION_DATA_FILES_MAP = {
    "orbitStateList": "orbit-state",
    "contactList": "contacts"
}

""" E2E Performance Simulator Flight Dynamics Provider Handler: File Manager """

def readCsvPropagationDataFiles(flightDynamicsDataPath: str, source: str = 'local', filesMap: dict = PROPAGATION_DATA_FILES_MAP) -> list:
    """ Read csv propagation data files and validate
        source 'local' from local repository, source 'remote' from remote git repository 
    """
    import glob
    propagationData = {}
    for propagationDataEntry, propgationDataFile in filesMap.items():
        #Build file name as convention /path/satId-stateTag.csv
        for filePath in glob.glob(os.path.join(flightDynamicsDataPath, "*_" + propgationDataFile + ".csv")):
            satId = filePath.split(os.sep)[-1].split("_")[0]
            if satId not in propagationData:
                propagationData[satId] = {}
            #Read from file
            if source == 'local':
                orbitDataParsed = readLocalCsvToDict(filePath)
            else:
                orbitDataParsed = readRemoteCsvToDict(filePath)
            propagationData[satId][propagationDataEntry] = orbitDataParsed
    if propagationData == {}:
        raise Exception("ERROR: in folder {}, no compatible Flight Dynamics Propagation Data found.".format(flightDynamicsDataPath))
    return propagationData

def readCsvPropagationDataFilesAsDataframe(flightDynamicsDataPath: str, source: str = 'local', filesMap: dict = PROPAGATION_DATA_FILES_MAP) -> pd.DataFrame:
    """ Read csv propagation data files and validate
        source 'local' from local repository, source 'remote' from remote git repository 
    """
    import glob
    propagationData = {}
    for propagationDataEntry, propgationDataFile in filesMap.items():
        #Build file name as convention /path/satId-stateTag.csv
        for filePath in glob.glob(os.path.join(flightDynamicsDataPath, "*_" + propgationDataFile + ".csv")):
            satId = filePath.split(os.sep)[-1].split("_")[0]
            if satId not in propagationData:
                propagationData[satId] = {}
            #Read from file
            if source == 'local':
                orbitDataParsed = readLocalCsvToDf(filePath)
            else:
                orbitDataParsed = readRemoteCsvToDf(filePath)
            propagationData[satId][propagationDataEntry] = orbitDataParsed
    if propagationData == {}:
        raise Exception("ERROR: in folder {}, no compatible Flight Dynamics Propagation Data found.".format(flightDynamicsDataPath))
    return propagationData

def savePropagationData(outputDataFolderPath: str, propagationData: AppResult):
    """ Save to output/data/flightdynamics """
    outputPath = getFlightDynamicsDataOutputPath(outputDataFolderPath)
    makeOutputFolder(outputPath)
    result = propagationData.result
    for satId in result:
        for propagationDataEntry, propgationDataFile in PROPAGATION_DATA_FILES_MAP.items():
            if propagationDataEntry not in result[satId]:
                result[satId][propagationDataEntry] = []
            saveListDictToCsv(result[satId][propagationDataEntry], os.path.join(outputPath, satId + "_" + propgationDataFile + ".csv"))
    return outputPath

def getFlightDynamicsDataOutputPath(outputDataFolderPath: str) -> str:
    return os.path.join(outputDataFolderPath, 'flightdynamics')

# -*- coding: utf-8 -*-