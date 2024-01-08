#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

import os

from ..utils.filemanager import makeOutputFolder, saveListDictToCsv

""" E2E Performance Simulator Air Link Budget Calculator Handler: File Manager """

def extractAirLinkDataFromCsv(simulationRequest: dict) -> dict:
    """ Read from repository required csv files and parse back to link data """
    def validateTime(orbitData: list, startTimestamp: int, endTimestamp: int, satId: str, stateTag: str):
        #TODO
        pass
    raise NotImplementedError

def saveAirLinkData(outputDataFolderPath: str, satId: str, airLinkData: dict):
    """ Save to output/data/airlink """
    outputPath = getAirLinkDataOutputPath(outputDataFolderPath)
    makeOutputFolder(outputPath)
    saveListDictToCsv(airLinkData, os.path.join(outputPath, satId + "_Air-Link-Data.csv"))
    return outputPath

def getAirLinkDataOutputPath(outputDataFolderPath: str) -> str:
    return os.path.join(outputDataFolderPath, 'airlink')

# -*- coding: utf-8 -*-