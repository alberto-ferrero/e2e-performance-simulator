#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

""" E2E Performance Simulator post processor """

import os

from ..postprocessor.plotter import plot
from ..postprocessor.writer import writeReport

def postProcessSimulationData(simulationRequest: dict,
                              outputPath: str,
                              flightDynamicsDataOutputPath: str,
                              linkDataOutputPath: str,
                              regulatoryDataOutputPath: str,
                              networkDataOutputPath: str,
                              airinterfaceDataOutputPath: str):
    """ Global post processor function, based on rules defined in the Simulation Request """
    # Produce plots
    outputPlotFolderPath = os.path.join(outputPath, 'plot')
    print(' - Writing plots to output folder: {}'.format(outputPlotFolderPath))
    plot(outputPlotFolderPath)

    # Produce reports
    outputReportFolderPath = os.path.join(outputPath, 'report')
    print(' - Writing reports to output folder: {}'.format(outputReportFolderPath))
    writeReport(simulationRequest,
                outputReportFolderPath,
                flightDynamicsDataOutputPath,
                linkDataOutputPath,
                regulatoryDataOutputPath,
                networkDataOutputPath,
                airinterfaceDataOutputPath,
                outputPlotFolderPath)

##################################################################################################################


# -*- coding: utf-8 -*-
