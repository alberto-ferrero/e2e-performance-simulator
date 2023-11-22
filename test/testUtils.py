#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

""" Test Utils """

import os
from ..src.orchestrator.main import main

def callSimulation(inputFile: str, clean: bool = True):
    """ Call Orchestrator to launch simulation as real case """
    outputPath = main(inputFile)
    if clean:
        cleanOutput(outputPath)
    return outputPath

def cleanOutput(outputPath: str):
    import shutil
    shutil.rmtree(outputPath)

def getBasePath() -> str:
    """ Get base path """
    currentPath = os.path.dirname(os.path.abspath(__file__))
    cpList = currentPath.split(os.sep)
    cpList.pop()
    cpList.pop()
    return os.sep.join(cpList)

def getTestInputPath() -> str:
    return os.path.join(getBasePath(), 'test', 'input')

def getTestRequestsPath() -> str:
    return os.path.join(getBasePath(), 'test', 'requests')

def checkFileInFolder(folderPath: str, re: str) -> bool:
    import glob
    return len(glob.glob(os.path.join(folderPath, re), recursive=True)) > 1

# -*- coding: utf-8 -*-