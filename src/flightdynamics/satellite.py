#! /usr/bin/env python3

# Copyright (C) 2023 Rivada Space Networks - SCC
# Author: aferrero

"""
    Collection of methods to write RSN Satellites objects
"""

mass = 480 #[kg]
Cd = 2.2
Cr = 1.8

def getGeometry() -> dict:
    """ Get standard geometry """
    return {
        "dimX": 1.0,
        "dimY": 0.25,
        "dimZ": 0.5,
        "shape": "parallelepiped"
    }

def getPropulsionSystem() -> tuple:
    """ Get standard propulsion system """
    th1 = {
        "id": "th-1",
        "Isp": 1472000,
        "thrust": 0.0376,
        "maxBurnTime": 13000000,
        "propellantMass": 30
    }
    return (th1, )

def getSolarArrays() -> tuple:
    """ Get standard solar arrays """
    sa1 = {
          "id": "solar-array-left",
          "surface": 2,
          "orientation": {
            "q0": 0.7071068,
            "q1": 0.0,
            "q2": -0.7071068,
            "q3": 0.0
          }
    }
    sa2 = {
          "id": "solar-array-right",
          "surface": 2,
          "orientation": {
            "q0": 0.7071068,
            "q1": 0.0,
            "q2": -0.7071068,
            "q3": 0.0
          }
    }
    return (sa1, sa2)