#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

""""
Collection of methods to manage files and folders.
"""

import os
import pandas as pd

def getBasePath() -> str:
    """ Get base path """
    currentPath = os.path.dirname(os.path.abspath(__file__))
    cpList = currentPath.split(os.sep)
    cpList.pop()
    cpList.pop()
    return os.sep.join(cpList)

def makeOutputFolder(outputFolderPath: str) -> str:
    """ Make output folder """
    try:
        os.makedirs(outputFolderPath)
    except:
        #output folder exists
        pass
    return outputFolderPath

def saveDictToCsv(data: dict, filePath: str):
    """ Save dictionary to file, as csv """
    df = pd.DataFrame.from_dict(data)
    df.to_csv(filePath)

def saveListDictToCsv(jsonList: list, filePath: str):
    """ Save dictionary list to file, as csv """
    df = pd.DataFrame(jsonList)
    df.to_csv(filePath)

def saveDictToJson(data: dict, filePath: str):
    """ Save dictionary to file, as json """
    import json
    with open(filePath, "w") as file:
        json.dump(data, file, indent=2)
    return filePath

def readLocalCsvToDict(filePath: str):
    """ Save dictionary reading csv from local folder """
    if os.path.isfile(filePath):
        try:
            df = pd.read_csv(filePath)
            return df.to_dict(index=False)
        except Exception as e:
            raise Exception('ERROR: impossible to open file and read as csv: {}, due to {}'.format(filePath, str(e)))
    else:
        raise Exception('ERROR: impossible to open file: {}'.format(filePath))

def readRemoteCsvToDict(filePath: str):
    """ Save dictionary reading csv from remote folder """ 
    try:
        df = pd.read_csv(filePath)
        return df.to_dict(index=False)
    except Exception as e:
        raise Exception('ERROR: impossible to open file and read as csv: {}, due to {}'.format(filePath, str(e)))