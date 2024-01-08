#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

import os

from ..utils.filemanager import makeOutputFolder, saveListDictToCsv

""" E2E Performance Simulator Space Link Budget Handler: File Manager """

def saveSpaceLinkData(outputDataFolderPath: str, satId: str, spacelinkData: dict):
    """ Save to output/data/spacelink """
    outputPath = getSpaceLinkDataOutputPath(outputDataFolderPath)
    makeOutputFolder(outputPath)
    saveListDictToCsv(spacelinkData, os.path.join(outputPath, satId + "_Space-Link-Data.csv"))
    return outputPath

def extractSpaceLinkDataFromCsv(simulationRequest: dict) -> dict:
    """ Read from repository required csv files and parse back to link data """
    def validateTime(orbitData: list, startTimestamp: int, endTimestamp: int, satId: str, stateTag: str):
        #TODO
        pass
    raise NotImplementedError

def getSpaceLinkDataOutputPath(outputDataFolderPath: str) -> str:
    return os.path.join(outputDataFolderPath, 'spacelink')

# -*- coding: utf-8 -*-