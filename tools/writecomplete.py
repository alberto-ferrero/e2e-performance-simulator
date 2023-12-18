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
numberOfUserTerminals = 0

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
            "id": "gs-ssc-kiruna",
            "location": {
                "latitude": 67.89,
                "longitude": 21.05,
                "altitude": 0,
            }, "antennas": [
                {
                    "id": "ant-1",
                    "band": "S"
                }
            ]
        },
        {
            "id": "gs-ssc-yatharagga",
            "location": {
                "latitude": -29.04,
                "longitude": 115.35,
                "altitude": 0,
            }, "antennas": [
                {
                    "id": "ant-1",
                    "band": "S"
                }
            ]
        },
        {
            "id": "gs-ssc-alaska",
            "location": {
                "latitude": 64.80,
                "longitude": -147.50,
                "altitude": 0,
            }, "antennas": [
                {
                    "id": "ant-1",
                    "band": "S"
                }
            ]
        },
        {
            "id": "gs-ssc-inuvik",
            "location": {
                "latitude": 68.32,
                "longitude": -133.55,
                "altitude": 0,
            }, "antennas": [
                {
                    "id": "ant-1",
                    "band": "S"
                }
            ]
        },
        {
            "id": "gs-ksat-hartebeesthoek",
            "location": {
                "latitude": -25.90,
                "longitude": 27.69,
                "altitude": 0,
            }, "antennas": [
                {
                    "id": "ant-1",
                    "band": "S"
                }
            ]
        },
        {
            "id": "gs-scc-santiago",
            "location": {
                "latitude": -33.15,
                "longitude": -70.67,
                "altitude": 0,
            }, "antennas": [
                {
                    "id": "ant-1",
                    "band": "S"
                }
            ]
        },
        {
            "id": "gs-ksat-svalbard",
            "location": {
                "latitude": 78.22,
                "longitude": 15.40,
                "altitude": 0,
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
                     nSatsPerPlane: int) -> list:
    """ Get list of satellites """
    # Generate satellites
    satellites = []
    for idPlane in range(1, nPlanes+1):
        for idSat in range(1, nSatsPerPlane+1):
            identifier = f"P{str(idPlane).zfill(2)}-{str(idSat).zfill(2)}"
            satellites.append(getRsnSatellite(
                identifier, date))

    return satellites


def getRsnSatellite(identifier: str, date: str) -> dict:
    """ Get asset satellite, with RSN Sat properties.
        Orbit data defiened by the identifier: #plane-#index.
    """
    return {
        # "archetype": "satellite",
        "id": f"rsn-A-{identifier}",
        "name": f"RSN Sat A {identifier}",
        "orbit": getOrbit(identifier, date),
        # "mass": 510,  # TBC no info from TO
        # "reflectionCoefficient": 1.8,
        # "dragCoefficient": 2.2,
        # "geometry": {
        #     "shape": "parallelepiped",
        #     "dimX": 1,  # TBC no info from TO
        #     "dimY": 0.25,  # TBC no info from TO
        #     "dimZ": 0.5  # TBC no info from TO
        # },
        # "solarArrays": getSolarArrays(),
        "antennas": getAntennas()
    }


def getOrbit(identifier: str, date: str, sma: float = 7428000, ecc: float = 0, inc: float = 89) -> dict:
    """ Get the orbit definition for the RSN Sat, based on the identifier:
            identifier = P#Plane-#sat
            Considering RAAN +X deg each plane, MA separation base on total satellites per plane
    """
    plane, index = identifier.split("-")
    plane = int(plane.replace('P', '')) - 1
    index = int(index) - 1
    M = dM * int(index) + 7.5 * (int(plane) % 2)
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
        # "orientation": {
        #       "q0": 1,
        #       "q1": 0.0,
        #       "q2": 0,
        #     "q3": 0.0
        # }
    }
    antKa = {
        "id": "antenna-Ka",
        "band": "Ka",
        # "orientation": {
        #       "q0": 1,
        #       "q1": 0.0,
        #       "q2": 0,
        #       "q3": 0.0
        # }
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
