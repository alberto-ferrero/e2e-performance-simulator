#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

""" E2E Performance Simulator Link Budget Calculator Handler: Antenna properties mapper """

def getSatelliteAntennaProperties(satBand: str):
    """ Get antenna properties for satellite """
    if satBand.lower() == 's':
        return {
            "txSize": 0.240, #[m]
            "rxSize": 0.159, #[m]
            "uplinkFrequency": 3.0 * 1e9, #[Hz]
            "downlinkFrequency": 2.0 * 1e9, #[Hz]
            "uplinkBandwidth": 100.0 * 1e6, #[Hz]
            "downlinkBandwidth": 8000.0 * 1e6 , #[Hz]
            "txPower": 20, #[W]
        }
    else:
        return {
            "txSize": 0.240, #[m]
            "rxSize": 0.159, #[m]
            "uplinkFrequency": 30.0 * 1e9, #[Hz]
            "downlinkFrequency": 20.0 * 1e9, #[Hz]
            "uplinkBandwidth": 100.0 * 1e6, #[Hz]
            "downlinkBandwidth": 8000.0 * 1e6 , #[Hz]
            "txPower": 20, #[W]
        }
 
def getUserTerminalAntennaProperties(utClass: str):
    """ Get antenna properties for user terminal """
    # if utClass.lower() == 'small':
    #     return {
    #         "GoT": 11.8, #[dB/K]
    #         "eirp": 46.5, #[dBW]
    #         "throughput": 100 #[Mbps]
    #     }
    # elif utClass.lower() == 'medium':
    #     return {
    #         "GoT": 16.8, #[dB/K]
    #         "eirp": 50.5, #[dBW]
    #         "throughput": 2000 #[Mbps]
    #     }
    # else:
    #     return {
    #         "GoT": 17.2, #[dB/K]
    #         "eirp": 55.5, #[dBW]
    #         "throughput": 10000 #[Mbps]
    #     }
    if utClass.lower() == 'small':
        return {
            "txSize": 0.240, #[m]
            "rxSize": 0.159, #[m]
            "txPower": .20, #[W]
        }
    elif utClass.lower() == 'medium':
        return {
            "txSize": 2.240, #[m]
            "rxSize": 2.159, #[m]
            "txPower": 20, #[W]
        }
    else:
       return {
            "txSize": 3.240, #[m]
            "rxSize": 3.159, #[m]
            "txPower": 24.20, #[W]
        }

def getGrounStationAntennaProperties(gsBand: str):
    """ Get antenna properties for ground stations """
    if gsBand.lower() == 's':
        return {
            "txSize": 3.240, #[m]
            "rxSize": 3.159, #[m]
            "txPower": 24.20, #[W]
        }
    else:
        return {
            "txSize": 3.240, #[m]
            "rxSize": 3.159, #[m]
            "txPower": 24.20, #[W]
        }

# -*- coding: utf-8 -*-