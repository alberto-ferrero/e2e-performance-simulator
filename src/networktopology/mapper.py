#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

""" E2E Performance Simulator Network Topology Handler: Antenna properties mapper """

def getSatelliteAntennaProperties(satBand: str):
    """ Get antenna properties for satellite """
    raise NotImplementedError
 
def getUserTerminalAntennaProperties(utClass: str):
    """ Get antenna properties for user terminal """
    raise NotImplementedError

def getGrounStationAntennaProperties(gsBand: str):
    """ Get antenna properties for ground stations """
    raise NotImplementedError

# -*- coding: utf-8 -*-