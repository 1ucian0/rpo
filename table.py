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
from tabulate import tabulate
from statistics import median as st_median
from statistics import stdev as st_stdev

parser = argparse.ArgumentParser(description='Generate table3.')
parser.add_argument('csvfile', metavar='file.csv', nargs=1, help='CSV file with results')
args = parser.parse_args()
csvfile = args.csvfile[0]

fields = ['level3_cxs', 'hoare_cxs', 'we_cxs', 'level3_depth', 'hoare_depth', 'we_depth', 'level3_single_gate', 'hoare_single_gate', 'we_single_gate', 'level3_time','hoare_time', 'we_time']


def median(data_string):
    return st_median([float(i) for i in data_string.strip('][').split(', ')])


def stdev(data_string):
    return st_stdev([float(i) for i in data_string.strip('][').split(', ')])


def maximun(data_string):
    return max([float(i) for i in data_string.strip('][').split(', ')])


def minimun(data_string):
    return min([float(i) for i in data_string.strip('][').split(', ')])


with open(csvfile, newline='') as csvfile:
    data = csv.DictReader(csvfile)
    result = []
    for no, row in enumerate(data):
        if not no:
            header = ['n_qubits',# 'level3_loop_iterations', 'we_loop_iterations',
                      'level3_cxs', 'hoare_cxs','we_cxs',
                      'level3_depth', 'hoare_depth', 'we_depth',
                      'level3_gate', 'hoare_gate', 'we_gate',
                      'level3_time','hoare_time', 'we_time',
                      'level3 time (stdev)', 'we time (stdev)',
                      'level3 time (min-max)', 'we time (min-max)']
        if not len(row):
            continue
        # we_iterations = median(row['we_loop_iterations'])
        # level3_iterations = median(row['level3_loop_iterations'])
        level3_cxs = median(row['level3_cxs'])
        hoare_cxs = median(row['hoare_cxs'])
        we_cxs = median(row['we_cxs'])
        level3_time = median(row['level3_time'])
        hoare_time = median(row['hoare_time'])
        we_time = median(row['we_time'])
        level3_depth = median(row['level3_depth'])
        hoare_depth = median(row['hoare_depth'])
        we_depth = median(row['we_depth'])
        level3_gate = median(row['level3_single_gate'])
        hoare_gate = median(row['hoare_single_gate'])
        we_gate = median(row['we_single_gate'])
        level3_time_sd = stdev(row['level3_time'])
        we_time_sd = stdev(row['we_time'])
        level3_time_mm = "%.5f - %.5f" % (minimun(row['level3_time']), maximun(row['level3_time']))
        we_time_mm = "%.5f - %.5f" % (minimun(row['we_time']), maximun(row['we_time']))

        result.append([row['n_qubits'], level3_cxs, hoare_cxs, we_cxs,
                       level3_depth, hoare_depth, we_depth,
                       level3_gate, hoare_gate, we_gate,
                       level3_time, hoare_time, we_time, level3_time_sd,
                       we_time_sd, level3_time_mm, we_time_mm])
    print(tabulate(result, headers=header))
