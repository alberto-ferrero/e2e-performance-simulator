#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

""" E2E Performance Simulator post processor """

import os

from ..postprocessor.writer import writeReport

from ...utils.results import AppResult

from ...flightdynamics.filemanager import savePropagationData
from ...linkbudget.filemanager import saveLinkData
from ...regulatorymapper.filemanager import saveRegulatorynData
from ...networktopology.filemanager import saveNetworkData
from ...airinterface.filemanager import saveAirTrafficData


def postProcessSimulationData(simulationRequest: dict,
                              outputFolderPath: str,
                              propagationDataRes: AppResult,
                              linkDataRes: AppResult,
                              regulatoryDataRes: AppResult,
                              networkDataRes: AppResult,
                              airtrafficDataRes: AppResult):
    """ Global post processor function, based on rules defined in the Simulation Request """
    # Save raw data for each module
    outputDataFolderPath = os.path.join(outputFolderPath, 'data')
    print(' - Saving raw simulations data to output folder: {}'.format(outputDataFolderPath))
    savePropagationData(outputDataFolderPath, propagationDataRes)
    saveLinkData(outputDataFolderPath, linkDataRes)
    saveRegulatorynData(outputDataFolderPath, regulatoryDataRes)
    saveNetworkData(outputDataFolderPath, networkDataRes)
    saveAirTrafficData(outputDataFolderPath, airtrafficDataRes)

    # Produce plots
    outputPlotFolderPath = os.path.join(outputFolderPath, 'plot')
    print(' - Writing plots to output folder: {}'.format(outputPlotFolderPath))

    # Produce reports
    outputReportFolderPath = os.path.join(outputFolderPath, 'report')
    print(' - Writing reports to output folder: {}'.format(outputReportFolderPath))
    writeReport(simulationRequest,
                outputReportFolderPath,
                outputDataFolderPath,
                outputPlotFolderPath)

##################################################################################################################


# -*- coding: utf-8 -*-
