#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (C) Copyright Ji Liu and Luciano Bello 2020.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

import argparse
import csv
import yaml
from importlib import import_module
from os import path

from benchmark.utils import Result

parser = argparse.ArgumentParser(description='Runs a benchmark.')
parser.add_argument('yamlfile', metavar='file.yaml', nargs=1, help='YAML configuration file')
args = parser.parse_args()
yamlfile = args.yamlfile[0]

with open(yamlfile) as file:
    configuration = yaml.load(file, Loader=yaml.FullLoader)

suite = import_module(configuration['suite'])
passmanagers = []
for pm_line in configuration['pass managers']:
    pm_module, pm_func = pm_line.split(':')
    passmanagers.append(getattr(import_module(pm_module), pm_func))

be_module, be_func = configuration.get('backend', 'qiskit.test.mock:FakeMelbourne').split(':')
backend = getattr(import_module(be_module), be_func)
fields = configuration['fields']
times = configuration.get('times', 1)
resultfile = path.join('results', '%s.csv' % path.basename(yamlfile).split('.')[0])

print('suite:', configuration['suite'])
print('backend:', backend)
print('pass managers:', ''.join(['\n\t' + pm for pm in configuration['pass managers']]))
print('fields:', ', '.join(fields))
print('times:', str(times))
print('result file:', resultfile)

with open(resultfile, 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fields)
    writer.writeheader()
    for circuit in suite.circuits():
        result = Result(circuit, backend)
        result.run_pms(passmanagers, times=times)
        # print(result.row(fields))
        writer.writerow(result.row(fields))
