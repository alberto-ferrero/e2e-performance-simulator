#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

import os

def run_all_tests():
    """Run all tests in folder, tests need to start with "test_"
       ./testResult as simulation output folder
       
       It creates result file in ./testResult

    """
    pathRes = './testResult/'
    try:
        os.mkdir(pathRes)
    except:
        pass

    #Call all test files
    os.system('pytest -s -v --log-cli-level=INFO -log-cli-format="%(levelname)s %(message)s" | tee ./testResult/vtResult.log')

##################################

if __name__ == '__main__':
    run_all_tests()

# -*- coding: utf-8 -*-