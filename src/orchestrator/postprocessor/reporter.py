#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

""" E2E Performance Simulator post processor reported """

import os
from ...flightdynamics.filemanager import savePropagationData
from ...linkbudget.filemanager import saveLinkData
from ...regulatorymapper.filemanager import saveRegulatorynData
from ...networktopology.filemanager import saveNetworkData
from ...airinterface.filemanager import saveAirTrafficData

def postProcess(simulationRequest: dict,
                outputFolderPath: str,
                propagationData: dict,
                linkData: dict,
                regulatoryData: dict,
                networkData: dict,
                airtrafficData: dict):
    """ Global post processor function, based on rules defined in the Simulation Request """
    #Save raw data for each module
    outputDataFolderPath = os.path.join(outputFolderPath, 'data')
    print(' - Saving raw simulations data to output folder: {}'.format(outputDataFolderPath))
    savePropagationData(outputDataFolderPath, propagationData)
    saveLinkData(outputDataFolderPath, linkData)
    saveRegulatorynData(outputDataFolderPath, regulatoryData)
    saveNetworkData(outputDataFolderPath, networkData)
    saveAirTrafficData(outputDataFolderPath, airtrafficData)

    #Produce plots
    outputPlotFolderPath = os.path.join(outputFolderPath, 'plot')
    print(' - Writing plots to output folder: {}'.format(outputPlotFolderPath))

    #Produce reports
    outputReportFolderPath = os.path.join(outputFolderPath, 'report')
    print(' - Writing reports to output folder: {}'.format(outputReportFolderPath))


##################################################################################################################


# -*- coding: utf-8 -*-