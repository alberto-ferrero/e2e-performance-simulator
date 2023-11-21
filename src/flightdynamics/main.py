#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

from ..flightdynamics.filemanager import readCsvPropagationDataFiles
from ..utils.timeconverter import getTimestampFromDate
from .request import propagate

""" E2E Performance Simulator Flight Dynamics Provider Handler """

def getFlightDynamicsPropagationData(simulationRequest: dict) -> dict:
    
    flightDynamicsInfo = simulationRequest['modules']['flightDynamics']

    #Define propagation data source
    if flightDynamicsInfo['data'] == 'run':
        print(' - Run Flight Dynamics propagation, calling server at {}'.format(flightDynamicsInfo['address']))

        #Get proagation request
        propagationRequest: dict = extractFlightDynamicsScenario(simulationRequest)
        print(' - Launch propagation of {} satellites, {} ground stations, {} user terminals'.format(len(simulationRequest['satellites']), len(simulationRequest['groundstations']), len(simulationRequest['userterminals'])))
        print(' - Propagating orbit from {} to {} ...'.format(simulationRequest['simulationWindow']['start'], simulationRequest['simulationWindow']['end']))
        return propagate(flightDynamicsInfo['address'], propagationRequest)
    
    else:
        print(' - Read Propagation Data from {} repository, at {}'.format(flightDynamicsInfo['data'], flightDynamicsInfo['address']))        

        #Read, validate and return propagation data
        return extractPropagationDataFromCsv(propagationRequest)


#######################################################################################################

def extractFlightDynamicsScenario(simulationRequest: dict) -> dict:
    """ From Simulation Request, extract information to build Flight Dynamics Propagation Request """

    def mapSatelliteOrbit(orbitObj: dict) -> dict:
        if orbitObj['type'] == "TLE":
            return orbitObj
        else:
            #Replace time from UTC time to UTC Epoch millis
            orbitObj['utcEpochMillis'] = getTimestampFromDate(orbitObj['utcTime'])
            orbitObj.pop('utcTime', None)
            return orbitObj

    propagationRequest = {}

    #Build scenario info
    propagationRequest['scenario'] = {
        'id': 'fd-' + simulationRequest['id'],
        "startTimestamp": getTimestampFromDate(simulationRequest['simulationWindow']['start']),
        "endTimestamp": getTimestampFromDate(simulationRequest['simulationWindow']['end']),
        "periodicUpdate": simulationRequest['modules']['flightDynamics']['properties']['periodicUpdate'],
        "propagator": {
            "type": simulationRequest['modules']['flightDynamics']['properties']['propagator']
        }
    }

    #Build satellites
    propagationRequest['assets'] = propagationRequest['assets'] = [
        {
            'id': sat['id'],
            'archetype': 'satellite',
            'orbit': mapSatelliteOrbit(sat['orbit']),
            'mass': sat.get('mass', None),
            'reflectionCoefficient': sat.get('reflectionCoefficient', None),
            'dragCoefficient': sat.get('dragCoefficient', None),
            'geometry': sat.get('geometry', None),
            'solarArrays': sat.get('solarArrays', []),
            'groundContacts': sat.get('groundContacts', []),
            'spaceContacts': sat.get('spaceContacts', [])
        }
      for sat in simulationRequest.get('satellites', [])
    ]

    #Build points of interest
    propagationRequest['pointsOfInterest'] = [
        {
            'id': poi['id'],
            'altitude': poi['location']['altitude'],
            'latitude': poi['location']['latitude'],
            'longitude': poi['location']['longitude']
        }
      for poi in simulationRequest.get('groundstations', []) + simulationRequest.get('userterminals', [])
    ]

    # TODO to add area of interest and angles crossing

    return propagationRequest

def extractPropagationDataFromCsv(simulationRequest: dict) -> dict:
    """ Read from repository required csv files and parse back to propagation data """
     
    def validateStateTime(orbitData: list, startTimestamp: int, endTimestamp: int, satId: str, stateTag: str):
        if getTimestampFromDate(orbitData[0]['utcTime']) != startTimestamp:
            raise Exception('ERROR: incopatible start propagation time {} in file containing {} for satellite {}'.format(orbitData[0]['utcTime'], stateTag, satId))
        if getTimestampFromDate(orbitData[-1]['utcTime']) != endTimestamp:
            raise Exception('ERROR: incopatible end propagation time {} in file containing {} for satellite {}'.format(orbitData[-1]['utcTime'], stateTag, satId))
    
    def validateContacts(contactsData: list, startTimestamp: int, endTimestamp: int, satId: str, argOfInterestIds: list, stateTag: str):
        for contact in contactsData:
            #Check time
            if 'utcTime' in contact and getTimestampFromDate(contact['utcTime']) < startTimestamp:
                raise Exception('ERROR: incopatible contact as prior start propagation time {} in file containing {} for satellite {}'.format(contact['utcTime'], stateTag, satId))
            elif 'startUtcTime' in contact and getTimestampFromDate(contact['startUtcTime']) < startTimestamp:
                raise Exception('ERROR: incopatible contact as prior start propagation time {} in file containing {} for satellite {}'.format(contact['startUtcTime'], stateTag, satId))
            if 'utcTime' in contact and getTimestampFromDate(contact['utcTime']) > endTimestamp:
                raise Exception('ERROR: incopatible contact as after end propagation time {} in file containing {} for satellite {}'.format(contact['utcTime'], stateTag, satId))
            elif 'endUtcTime' in contact and getTimestampFromDate(contact['startUtcTime']) > endTimestamp:
                raise Exception('ERROR: incopatible contact as after end propagation time {} in file containing {} for satellite {}'.format(contact['endUtcTime'], stateTag, satId))
            #Compatible argument of interest
            if contact['argumentOfInterestId'] not in argOfInterestIds:
                raise Exception('ERROR: incopatible contact as not supported argument of interest id {} in file containing {} for satellite {}'.format(contact['argumentOfInterestId'], stateTag, satId))

    def validateSatelliteIds(propagationData: dict, satIds: list):
        propSatIds = set([satId for satId in propagationData])
        if propSatIds != set(satIds):
            raise Exception('ERROR: requested satellites from Simulation Request ({}) are not matching the propagated data from files ({})'.format(set(satIds), propSatIds))

    #Get simulation time
    startTimestamp = getTimestampFromDate(simulationRequest['simulationWindow']['start'])
    endTimestamp = getTimestampFromDate(simulationRequest['simulationWindow']['end'])

    #Get list of assets
    satIds = [satId for satId in simulationRequest['satellites']]
    
    #Build Propagation Data object reading from stored files
    propagationData = {}
    for satellite in simulationRequest['satellites']:
        satId = satellite['id']
        propagationData[satId] = {}
        propagationData[satId] = readCsvPropagationDataFiles(simulationRequest, satId)

        #Validate
        for orbitDataTag, orbitData in propagationData[satId].items():
            if 'State' in orbitDataTag:
                validateStateTime(orbitData, startTimestamp, endTimestamp, satId, orbitDataTag)
            if 'contact' in orbitDataTag:
                #Get arguments of interest for satellite
                groundContacts = set(satellite.get('groundContacts', []))
                spaceContacts = set(satellite.get('spaceContacts', []))
                validateContacts(orbitData, startTimestamp, endTimestamp, satId, groundContacts + spaceContacts, orbitDataTag)
    
    #Validate satellites
    validateSatelliteIds(propagationData, satIds)

# -*- coding: utf-8 -*-