#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

""""
Collection of methods to manage files and folders.
"""

import os
import pandas as pd
import yaml
import json
import re

def getBasePath() -> str:
    """ Get base path """
    currentPath = os.path.dirname(os.path.abspath(__file__))
    cpList = currentPath.split(os.sep)
    cpList.pop()
    cpList.pop()
    return os.sep.join(cpList)

def getLogoPath() -> str:
    return os.path.join(getBasePath(), "src", "orchestrator", "postprocessor", "logo")

def makeOutputFolder(outputFolderPath: str) -> str:
    """ Make output folder """
    try:
        os.makedirs(outputFolderPath)
    except:
        #output folder exists
        pass
    return outputFolderPath

def removeFolder(folderPath: str):
    import shutil
    shutil.rmtree(folderPath, ignore_errors=True)

def saveDictToCsv(data: dict, filePath: str):
    """ Save dictionary to file, as csv """
    df = pd.DataFrame.from_dict(data)
    df.to_csv(filePath, index=False)

def saveListDictToCsv(jsonList: list, filePath: str):
    """ Save dictionary list to file, as csv """
    df = pd.DataFrame(jsonList)
    df.to_csv(filePath, index=False)

def saveDictToJson(data: dict, filePath: str):
    """ Save dictionary to file, as json """
    import json
    with open(filePath, "w") as file:
        json.dump(data, file, indent=2)
    return filePath

def readLocalCsvToDict(filePath: str) -> list:
    """ Save dictionary reading csv from local folder """
    if os.path.isfile(filePath):
        try:
            df = pd.read_csv(filePath)
            return df.T.apply(lambda x: x.dropna().to_dict()).tolist()
        except pd.errors.EmptyDataError:
            return []
        except Exception as e:
            raise Exception('ERROR: impossible to open file and read as csv: {}, due to {}'.format(filePath, str(e)))
    else:
        raise Exception('ERROR: impossible to open file: {}'.format(filePath))

def readLocalCsvToDf(filePath: str) -> pd.DataFrame:
    """ Save dictionary reading csv from local folder """
    if os.path.isfile(filePath):
        try:
            df = pd.read_csv(filePath)
            return df
        except pd.errors.EmptyDataError:
            return []
        except Exception as e:
            raise Exception('ERROR: impossible to open file and read as csv: {}, due to {}'.format(filePath, str(e)))
    else:
        raise Exception('ERROR: impossible to open file: {}'.format(filePath))

def readRemoteCsvToDict(filePath: str) -> list:
    """ Save dictionary reading csv from remote folder """ 
    try:
        df = pd.read_csv(filePath)
        return df.T.apply(lambda x: x.dropna().to_dict()).tolist()
    except pd.errors.EmptyDataError:
            return []
    except Exception as e:
        raise Exception('ERROR: impossible to open file and read as csv: {}, due to {}'.format(filePath, str(e)))

def readRemoteCsvToDf(filePath: str) -> pd.DataFrame:
    """ Save dictionary reading csv from remote folder """ 
    try:
        df = pd.read_csv(filePath)
        return df
    except pd.errors.EmptyDataError:
            return []
    except Exception as e:
        raise Exception('ERROR: impossible to open file and read as csv: {}, due to {}'.format(filePath, str(e)))

def readInputYmlFile(inputFilePath: str) -> dict:
    # Try to open as yaml
    try:
        with open(inputFilePath) as scenarioYaml:

            def add_bool(self, node):
                """Custom FullLoader for yaml files, overwriting the bolean conversion"""
                value: str = self.construct_scalar(node)
                if value.lower() in ['true', 'false']:
                    return self.bool_values[value.lower()]
                else:
                    return value

            loader = yaml.FullLoader
            loader.add_constructor(u'tag:yaml.org,2002:bool', add_bool)
            loader.add_implicit_resolver(
                    u'tag:yaml.org,2002:float',
                    re.compile(u'''^(?:
                        [-+]?(?:[0-9][0-9_]*)\\.[0-9_]*(?:[eE][-+]?[0-9]+)?
                    |[-+]?(?:[0-9][0-9_]*)(?:[eE][-+]?[0-9]+)
                    |\\.[0-9_]+(?:[eE][-+][0-9]+)?
                    |[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+\\.[0-9_]*
                    |[-+]?\\.(?:inf|Inf|INF)
                    |\\.(?:nan|NaN|NAN))$''', re.X),
                    list(u'-+0123456789.'))
            return yaml.load(scenarioYaml, Loader=loader)

    except Exception as e:
        #Raise error
        raise Exception('ERROR: not possible to parse input yaml file due to: {}'.format(str(e)))
    
def readInputJsonFile(inputFilePath: str) -> dict:
    # Try to open as json
    try:
        with open(inputFilePath) as scenarioJson:
            return json.load(scenarioJson)
    except Exception as e:
        #Raise error
        raise Exception('ERROR: not possible to parse input json file due to: {}'.format(str(e)))