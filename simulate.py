#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

""" Launch E2E Perfomance Simulation, running from the Simulation Request configuration file """

###############################################################################

if __name__ == "__main__":
    from src.orchestrator.main import main
    import argparse
    parser = argparse.ArgumentParser(description="Run E2E Performance Simulator")
    parser.add_argument('-i', '--input', type=str, help="E2E Simulation Request configuration file", required=True)
    args = parser.parse_args()
    main(args.input)
