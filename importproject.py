#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

""" Import E2E Project strutcture """

from sys import path as syspath
from os import path

#Import working folders
basepath : str = path.abspath(path.dirname(path.realpath(__file__)))

#Import Utils
syspath.insert(0, path.join(basepath, 'utils'))

#Import Orchestrator
syspath.insert(0, path.join(basepath, 'orchestrator'))
syspath.insert(0, path.join(basepath, 'orchestrator', 'preprocessor'))
syspath.insert(0, path.join(basepath, 'orchestrator', 'postprocessor'))

#Import Handlers files
syspath.insert(0, path.join(basepath, 'airinterface'))
syspath.insert(0, path.join(basepath, 'flightdynamics'))
syspath.insert(0, path.join(basepath, 'linkbudget'))
syspath.insert(0, path.join(basepath, 'networktopology'))
syspath.insert(0, path.join(basepath, 'regulatorymapper'))
syspath.insert(0, path.join(basepath, 'regulatorymapper'))
