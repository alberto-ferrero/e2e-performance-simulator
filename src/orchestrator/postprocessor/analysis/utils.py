#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

""" E2E Performance Simulator Analysis: utilty methods """

def getItalXConnections(satId: str) -> list:
    """ Get Ital X connection, based on satellite id rsn-sat-#plane-#sat-#satXplane-#planes"""
    rsn, satId, plane, sat, totSats, totPlanes = satId.split("-")

    planeM = str(int(plane) - 1 if int(plane) - 1 > 0 else int(totPlanes) - 1)
    planeP = str(int(plane) + 1 if int(plane) + 1 < int(totPlanes) else 0)

    satM = str(int(sat) - 1 if int(sat) - 1 > 0 else int(totSats) - 1)
    satP = str(int(sat) + 1 if int(sat) + 1 < int(totSats) else 0)

    return ("-".join([rsn, satId, plane, satP, totSats, totPlanes]),
            "-".join([rsn, satId, plane, satM, totSats, totPlanes]),
            "-".join([rsn, satId, planeM, sat, totSats, totPlanes]),
            "-".join([rsn, satId, planeP, sat, totSats, totPlanes]))

def getFlatXConnections(satId: str) -> list:
    """ Get Flat X connection, based on satellite id rsn-sat-#plane-#sat-#satXplane-#planes"""
    rsn, satId, plane, sat, totSats, totPlanes = satId.split("-")

    planeM = str(int(plane) - 1 if int(plane) - 1 > 0 else int(totPlanes) - 1)
    planeP = str(int(plane) + 1 if int(plane) + 1 < int(totPlanes) else 0)

    satM = str(int(sat) - 1 if int(sat) - 1 > 0 else int(totSats) - 1)
    satP = str(int(sat) + 1 if int(sat) + 1 < int(totSats) else 0)

    return ("-".join([rsn, satId, planeM, sat, totSats, totPlanes]),
            "-".join([rsn, satId, planeM, satP, totSats, totPlanes]),
            "-".join([rsn, satId, planeP, sat, totSats, totPlanes]),
            "-".join([rsn, satId, planeP, satM, totSats, totPlanes]))

# -*- coding: utf-8 -*-