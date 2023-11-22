#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

""" Test to cover Flight Dynamics Hanlder and Flight Dynamics Servers """

import requests_mock

import os
import json
from testUtils import callSimulation, cleanOutput
from testUtils import getTestInputPath, getTestRequestsPath, checkFileInFolder

def test_01_request_FD_Orekit_run(requests_mock):
    """
        Test: launch E2E Perfomance Simulation, check that:
        - Orekit FD library has been called
        - data has been saved
    """
    fdOrekitUrl = "http://localhost:8081/flight-dynamics/api/v1/propagation-data"
    
    #Define Mock properties
    inputFile = os.path.join(getTestInputPath(), 'simulation-request-test-fd.yml')
    with open(os.path.join(getTestRequestsPath(), 'test-fd-request.json')) as f:
        expectedPropagationRequest = json.load(f)
    with open(os.path.join(getTestRequestsPath(), 'test-fd-orekit-response.json')) as f:
        mockedPropagationResponse = json.load(f)
    requests_mock.post(fdOrekitUrl, json=mockedPropagationResponse)

    #Call simulation
    outputPath = callSimulation(inputFile)

    #Assert that the request body matches the data variable
    assert requests_mock.adapter.last_request.json() == expectedPropagationRequest
    assert requests_mock.adapter.request_history[-1].json() == expectedPropagationRequest

    #Asser FD data has been created
    for sat in expectedPropagationRequest['satellites']:
        assert checkFileInFolder(outputPath, sat['id'] + "_orbit-state.csv")
        assert checkFileInFolder(outputPath, sat['id'] + "_contacts.csv")

    #Clean folder
    cleanOutput(outputPath)


def test_02_request_FD_Orekit_read_from_local():
    """
        Test: launch E2E Perfomance Simulation, check that:
        - FD data is taken from the local folder
    """
    pass

# -*- coding: utf-8 -*-