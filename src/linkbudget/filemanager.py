#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

import os

from ..utils.results import AppResult
from ..utils.filemanager import makeOutputFolder, saveListDictToCsv

""" E2E Performance Simulator Link Budget Calculator Handler File Manager """

def extractLinkDataFromCsv(simulationRequest: dict) -> dict:
    """ Read from repository required csv files and parse back to link data """
     
    def validateTime(orbitData: list, startTimestamp: int, endTimestamp: int, satId: str, stateTag: str):
        #TODO
        pass
    raise NotImplementedError

def saveLinkData(outputDataFolderPath: str, linkDataFull: dict):
    """ Save to output/data/linkbudget """
    outputPath = os.path.join(outputDataFolderPath, 'linkbudget')
    makeOutputFolder(outputPath)
    for satId in linkDataFull:
        saveListDictToCsv(linkDataFull[satId], os.path.join(outputPath, satId + "_Link-Data.csv"))
    return outputPath

# -*- coding: utf-8 -*-