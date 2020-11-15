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

import pandas as pd
import matplotlib.pylab as plt
from benchmark.utils import median_cell, legends
import argparse

parser = argparse.ArgumentParser(description='Generate graphs randomly generated circuits.')
parser.add_argument('csvfile', metavar='file.csv', nargs=1, help='CSV file with results')
args = parser.parse_args()
csvfile = args.csvfile[0]

fields = ['level3_cxs', 'we_cxs', 'level2_cxs',
          'level3_time', 'we_time', 'level2_time']

data = pd.read_csv(csvfile, index_col='depth',
                   usecols=['depth', 'n_qubits',
                            'level3_cxs', 'we_cxs', 'level2_cxs',
                            'level3_time', 'we_time', 'level2_time'])
for field in fields:
    median_cell(data, field)

# CX count
for name, groupin in data.groupby('n_qubits'):
    ax = groupin[['level3_cxs_median', 'we_cxs_median', 'level2_cxs_median']].plot()
    ax.set_ylabel("# CNot gates")
    ax.lines[0].set_dashes([2])
    ax.lines[2].set_dashes([3, 1])
    plt.legend([legends['qiskit_level3'],
                legends['rpo_level3'],
                legends['qiskit_level2']])
    ax.set_title(str(name) + '-qubit circuits')
    plt.savefig(str(name) + '_cx_depth.pdf')

# transpilation time
for name, groupin in data.groupby('n_qubits'):
    ax = groupin[['level3_time_median', 'we_time_median', 'level2_time_median']].plot()
    ax.lines[0].set_dashes([2])
    ax.lines[2].set_dashes([3, 1])
    ax.set_ylabel("transpilation time (seconds)")
    plt.legend([legends['qiskit_level3'],
                legends['rpo_level3'],
                legends['qiskit_level2']])
    ax.set_title(str(name) + '-qubit circuits')
    plt.savefig(str(name) + '_time.pdf')
