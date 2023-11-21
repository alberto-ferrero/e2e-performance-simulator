#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

""" 

Rivada Space Network End-to-End Performance Simulator 

The E2E Performance Simulator runs in modular way, calling different sub-modules
to determine the performances of the system.

This is the main Orchestrator function, that:
- parses the Simulation request and extracts the simulation constraints
- run the simulation calling the required sub-moduele or retrieving existing pre comupted data
- perform post processing

"""

import os
import time
from datetime import datetime
from ..utils.results import AppResult
from ..utils.filemanager import getBasePath, makeOutputFolder

#Import Orchestrator modules
from .preprocessor.configparser import getSimulationRequest
from .postprocessor.reporter import postProcess

#Import Handlers
from ..flightdynamics.main import getFlightDynamicsPropagationData
from ..linkbudget.main import getLinkBudgetData
from ..networktopology.main import getNetworkTopologyData
from ..regulatorymapper.main import getRegulatoryMapperData
from ..airinterface.main import getAirInterfaceAnalysisData

    
def main(inputFile: str):
    """Main Orchestrator function call"""

    print('\nWelcome to RSN E2E Performance Simulator\n')
    tick = time.time()
    init = tick

    #Parse input simulation request
    inputFileAbsPath = os.path.abspath(inputFile)
    print(' - Reading input scenario file: {}'.format(inputFileAbsPath))
    simulationRequest: dict = getSimulationRequest(inputFileAbsPath)

    #Build output folder
    simId = datetime.fromtimestamp(tick).strftime("%Y-%m-%d_%H-%M-%S") + "_" + simulationRequest['id']
    outputPath = makeOutputFolder(os.path.join(getBasePath(), 'output', simId))

    #Call Handlers if requested by the modules
    if 'flightDynamics' in simulationRequest['modules']:
        print(' - Getting Flight Dynamics Data {}'.format(textDataFrom(simulationRequest['modules']['flightDynamics']['data'])))
        propagationDataRes: AppResult = getFlightDynamicsPropagationData(simulationRequest)
        print(' - Flight Dynamics Data generated in {:.4f} seconds'.format(time.time() - tick))
        tick = time.time()
    else:
        propagationDataRes = AppResult(200, {})

    if 'linkBudget' in simulationRequest['modules']:
        print(' - Getting Link Budget Data {}'.format(textDataFrom(simulationRequest['modules']['linkBudget']['data'])))
        linkDataRes: AppResult = getLinkBudgetData(simulationRequest)
        print(' - Link Budget Data generated in {:.4f} seconds'.format(time.time() - tick))
        tick = time.time()
    else:
        linkDataRes = AppResult(200, {})

    if 'regulatoryMap' in simulationRequest['modules']:
        print(' - Getting Regulatory Data {}'.format(textDataFrom(simulationRequest['modules']['regulatoryMap']['data'])))
        regulatoryDataRes: AppResult = getRegulatoryMapperData(simulationRequest)
        print(' - Regulatory Data generated in {:.4f} seconds'.format(time.time() - tick))
        tick = time.time()
    else:
        regulatoryDataRes = AppResult(200, {})

    if 'networkTopology' in simulationRequest['modules']:
        print(' - Getting Network Topology Data {}'.format(textDataFrom(simulationRequest['modules']['networkTopology']['data'])))
        networkDataRes: AppResult = getNetworkTopologyData(simulationRequest)
        print(' - Network Topology Data generated in {:.4f} seconds'.format(time.time() - tick))
        tick = time.time()
    else:
        networkDataRes = AppResult(200, {})

    if 'airInterface' in simulationRequest['modules']:
        print(' - Getting Air Interface Data {}'.format(textDataFrom(simulationRequest['modules']['airInterface']['data'])))
        airinterfaceDataRes: AppResult = getAirInterfaceAnalysisData(simulationRequest)
        print(' - Air Interface Data generated in {:.4f} seconds'.format(time.time() - tick))
        tick = time.time()
    else:
        airinterfaceDataRes = AppResult(200, {})

    print(' - E2E Simulation run completed in {:.4f} seconds'.format(time.time() - init))
    tick = time.time()

    #Post Processing and generating perfomance output
    postProcess(simulationRequest, 
                outputPath,
                propagationDataRes.result,
                linkDataRes.result,
                regulatoryDataRes.result,
                networkDataRes.result,
                airinterfaceDataRes.result)
    
    print(' - E2E Simulation post processing completed in in {:.4f} seconds\n'.format(time.time() - init))


###############################################################################

def textDataFrom(tag: str) -> str:
    if tag == 'run':
        return "running calculation from server"
    else:
        return "from stored {} repository".format(tag)

# -*- coding: utf-8 -*-