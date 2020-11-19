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


parser = argparse.ArgumentParser(description='Generate graphs for QPE cx count and time.')
parser.add_argument('csvfiles', metavar='file.csv',
                    nargs='+',
                    help='CSV file with results')
args = parser.parse_args()

fields = ['level3_cxs', 'we_cxs', 'level3_time', 'we_time']

for csvfile in args.csvfiles:
    data = pd.read_csv(csvfile, index_col='n_qubits',
                       usecols=['depth', 'n_qubits', 'level3_cxs', 'we_cxs', 'level3_time',
                                'we_time'])

    for field in fields:
        median_cell(data, field)

    # CX count
    ax = data[['level3_cxs_median', 'we_cxs_median']].plot()
    ax.set_ylabel("# CNot gates")
    ax.set_xlabel("size (amount of qubits)")
    ax.lines[0].set_dashes([3, 1])
    plt.legend([legends['qiskit_level3'],
                legends['rpo_level3']])
    plt.savefig('qpe_' + csvfile.split('.', 1)[0].split('_')[1] + '_cx_depth.pdf')

    # transpilation time
    ax = data[['level3_time_median', 'we_time_median']].plot()
    ax.lines[0].set_dashes([3, 1])
    ax.set_ylabel("transpilation time (seconds)")
    ax.set_xlabel("size (amount of qubits)")
    plt.legend([legends['qiskit_level3'],
                legends['rpo_level3']])
    plt.savefig('qpe_' + csvfile.split('.', 1)[0].split('_')[1] + '_time.pdf')
