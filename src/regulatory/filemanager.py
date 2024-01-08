#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

import os

from ..utils.results import AppResult

""" E2E Performance Simulator Regulatory Mapper Handler: File Manager """

def saveRegulatoryData(outputDataFolderPath: str, regulatoryData: AppResult):
    pass

def getRegulatoryDataOutputPath(outputDataFolderPath: str) -> str:
    return os.path.join(outputDataFolderPath, 'regulatory')

# -*- coding: utf-8 -*-