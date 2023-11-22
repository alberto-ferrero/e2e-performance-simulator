#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

from ...utils.filemanager import getBasePath
from jsonschema import validate
import yaml
import json
import re
import os

""" E2E Performance Simulator pre processor """

def preProcessSimulationRequest(inputFilePath: str) -> dict:
    """ Read input file and extrac Simulation Request as dictionary """
    #Read file
    simulationRequest = readSimulationRequest(inputFilePath)

    #Validate structure
    simulationRequest = validateSimulationRequest(simulationRequest)

    #Return
    return simulationRequest

################################################################################################

def readSimulationRequest(inputFilePath: str) -> dict:
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
        raise Exception('ERROR: not possible to parse input Simulation Request due to: {}'.format(str(e)))

def validateSimulationRequest(simulationRequest: dict) -> dict:
    try:
        #Set validation schema
        simulationRequestSchema = os.path.join('api', 'simulationrequest-schema.json')
        #Validate with schema
        with open(os.path.join(getBasePath(), simulationRequestSchema), "r") as f: 
            validate(instance=simulationRequest, schema=json.load(f))

        #Additional validation, check compatibility of arguments
        sats = simulationRequest.get('satellites', [])
        gss = simulationRequest.get('groundstations', [])
        uts = simulationRequest.get('userterminals', [])
        satIds = set([sat['id'] for sat in sats])
        groundIds = set([i['id'] for i in uts + gss])
        for satellite in sats:
            groundContacts = set(satellite.get('groundContacts', []))
            spaceContacts = set(satellite.get('spaceContacts', []))
            if not groundContacts.issubset(groundIds):
                raise Exception('for satellite {}, ground contacts ({}) are referring to not existent ground asset ({})'.format(satellite['id'], groundContacts, groundIds))
            if not spaceContacts.issubset(satIds):
                raise Exception('for satellite {}, space contacts ({}) are referring to not existent satellite ({})'.format(satellite['id'], groundContacts, groundIds))
            
        return simulationRequest
    
    except Exception as e:
        #Raise error
        raise Exception('ERROR: validation of Simulation Request failed due to: {}'.format(str(e)))

# -*- coding: utf-8 -*-