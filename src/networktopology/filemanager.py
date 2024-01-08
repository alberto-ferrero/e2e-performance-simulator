#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

import os

from ..utils.results import AppResult

""" E2E Performance Simulator Network Topology Handler: File Manager """

def saveNetworkData(outputDataFolderPath: str, networkData: AppResult):
    pass

def getNetworkDataOutputPath(outputDataFolderPath: str) -> str:
    return os.path.join(outputDataFolderPath, 'network')

# -*- coding: utf-8 -*-