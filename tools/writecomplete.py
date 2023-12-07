""" E2E Performance Simulator Tool: write complete set of assets """

import os
import yaml
from random import randrange

###############################################################################################

# Fix parameters
date = "2026-01-01T00:00:00.00"

# Number of Satellites
satellitesPerPlane = 24
numberOfPlanes = 12

# Geometry
dRAAN = 180 / numberOfPlanes
dM = 360 / satellitesPerPlane

# Number of groundstaitons (random)
numberOfGroundStations = 1

# Number of userterminals (random)
numberOfUserTerminals = 5

###############################################################################################

def getBasePath() -> str:
    """ Get base path """
    currentPath = os.path.dirname(os.path.abspath(__file__))
    cpList = currentPath.split(os.sep)
    cpList.pop()
    return os.sep.join(cpList)

def getLogoPath() -> str:
    return os.path.join(getBasePath(), "src", "orchestrator", "postprocessor", "logo")

def makeOutputFolder(outputFolderPath: str) -> str:
    """ Make output folder """
    try:
        os.makedirs(outputFolderPath)
    except:
        # output folder exists
        pass
    return outputFolderPath

###############################################################################################

def getUts(n: int) -> list:
    """ Get list of User Terminal, random location
    """
    classes = ["small", "medium", "large"]
    uts = []
    for index in range(n):
        uts.append(
            {
                "id": f"ut-{index}",
                "location": {
                    "latitude": randrange(-90, 91),
                    "longitude": randrange(-180, 181),
                    "altitude": randrange(0, 10000)
                },
                "class": classes[randrange(0, 3)],
                "connections": []
            }
        )
    return uts

def getGss(n: int) -> list:
    """ Get list of Ground Stations, random location and LEOP stations
    """
    gss = [
        {
            "id": "gs-svalbard",
            "location": {
                "latitude": 78.15,
                "longitude": 16.03,
                "altitude": 300,
            }, "antennas": [
                {
                    "id": "ant-1",
                    "band": "S"
                }
            ]
        },
        {
            "id": "gs-chile",
            "location": {
                "latitude": -53.08,
                "longitude": -70.88,
                "altitude": 0,
            }, "antennas": [
                {
                    "id": "ant-1",
                    "band": "S"
                }
            ]
        },
        {
            "id": "gs-cape-town",
            "location": {
                "latitude": -33.98,
                "longitude": 18.81,
                "altitude": 0,
            }, "antennas": [
                {
                    "id": "ant-1",
                    "band": "S"
                }
            ]
        },
        {
            "id": "gs-hartebeesthoek",
            "location": {
                "latitude": -25.67,
                "longitude": 28.05,
                "altitude": 39,
            }, "antennas": [
                {
                    "id": "ant-1",
                    "band": "S"
                }
            ]
        },
        {
            "id": "gs-wellington",
            "location": {
                "latitude": -41.3133,
                "longitude": 174.74,
                "altitude": 139,
            }, "antennas": [
                {
                    "id": "ant-1",
                    "band": "S"
                }
            ]
        },
        {
            "id": "gs-peterborough",
            "location": {
                "latitude": -32.9004,
                "longitude": 138.93,
                "altitude": 4.3,
            }, "antennas": [
                {
                    "id": "ant-1",
                    "band": "S"
                }
            ]
        }
    ]
    for index in range(n):
        gss.append(
            {
                "id": f"gs-{index}",
                "location": {
                    "latitude": randrange(-90, 91),
                    "longitude": randrange(-180, 181),
                    "altitude": randrange(0, 10000),
                },
                "antennas": [
                    {
                        "id": "ant-1",
                        "band": "S"
                    },
                    {
                        "id": "ant-0",
                        "band": "Ka"
                    }
                ]
            }
        )
    return gss

def getRsnSatellites(date: str,
                     nPlanes: int,
                     nSatsPerPlane: int,
                     groundContacts: list) -> list:
    """ Get list of satellites """
    # Generate satellites
    satellites = []
    for idPlane in range(nPlanes):
        for idSat in range(nSatsPerPlane):
            identifier = f"P{str(idPlane).zfill(2)}-{str(idSat).zfill(2)}"
            satellites.append(getRsnSatellite(
                identifier, date, groundContacts))

    return satellites

def getRsnSatellite(identifier: str, date: str, groundContacts: list) -> dict:
    """ Get asset satellite, with RSN Sat properties.
        Orbit data defiened by the identifier: #plane-#index.
    """
    #Warning! adding all groundstations and userterminals as contacts
    groundContacts = [it['id'] for it in groundstations + userterminals]
    #groundContacts = []
    return {
        "archetype": "satellite",
        "id": f"rsn-A-{identifier}",
        "name": f"RSN Sat A {identifier}",
        "orbit": getOrbit(identifier, date),
        "mass": 510,  # TBC no info from TO
        "reflectionCoefficient": 1.8,
        "dragCoefficient": 2.2,
        "geometry": {
            "shape": "parallelepiped",
            "dimX": 1,  # TBC no info from TO
            "dimY": 0.25,  # TBC no info from TO
            "dimZ": 0.5  # TBC no info from TO
        },
        "solarArrays": getSolarArrays(),
        "antennas": getAntennas(),
        "groundContacts": groundContacts
    }

def getOrbit(identifier: str, date: str, sma: float = 7428000, ecc: float = 0, inc: float = 89) -> dict:
    """ Get the orbit definition for the RSN Sat, based on the identifier:
            identifier = P#Plane-#sat
            Considering RAAN +X deg each plane, MA separation base on total satellites per plane
    """
    plane, index = identifier.split("-")
    plane = plane.replace('P', '')
    deltaM = int(plane) % 2 * dM / 2.0
    M = dM * int(index) + deltaM
    return {
        "type": "BLSKEPLERIAN",
        "referenceFrame": "EME2000",
        "utcTime": date,
        "semiMajorAxis": sma,
        "eccentricity": ecc,
        "inclination": inc,
        "rightAscensionAscendingNode": dRAAN * int(plane),
        "argumentPeriapsis": 0,
        "meanAnomaly": M - 360 if M > 360 else M
    }

def getSolarArrays() -> list:
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
    return [sa1, sa2]

def getAntennas() -> list:
    """ Get standard antennas """
    antS = {
        "id": "antenna-S",
        "band": "S",
        "orientation": {
              "q0": 1,
              "q1": 0.0,
              "q2": 0,
            "q3": 0.0
        }
    }
    antKa = {
        "id": "antenna-Ka",
        "band": "Ka",
        "orientation": {
              "q0": 1,
              "q1": 0.0,
              "q2": 0,
              "q3": 0.0
        }
    }
    return [antS, antKa]

###################################################################################################
# MAIN

# Write to output/tmp
outputTmpPath = os.path.join(getBasePath(), 'output', 'tmp')
makeOutputFolder(outputTmpPath)

# Generate groundstations
groundstations = getGss(numberOfGroundStations)

# Generate userterminals
userterminals = getUts(numberOfUserTerminals)

# Generate satellites
satellites = getRsnSatellites(date=date,
                              groundContacts=groundstations + userterminals,
                              nPlanes=numberOfPlanes,
                              nSatsPerPlane=satellitesPerPlane)

# All assets
assets = {
    "satellites": satellites,
    "groundstations": groundstations,
    "userterminals": userterminals
}

# Dump file
scenarioFile = os.path.join(
    outputTmpPath, 'simulationrequest-complete-assets.yml')
with open(scenarioFile, 'w') as outfile:
    yaml.dump(assets, outfile, default_flow_style=False)

print("\nGenerated in {}\n".format(scenarioFile))
