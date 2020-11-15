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

import matplotlib
import matplotlib.pylab as plt
from statistics import median

fontsize = 15

plt.style.use('grayscale')

matplotlib.rcParams['mathtext.fontset'] = 'stix'
matplotlib.rcParams['axes.labelsize'] = fontsize
matplotlib.rcParams['xtick.labelsize'] = fontsize
matplotlib.rcParams['ytick.labelsize'] = fontsize
matplotlib.rcParams['legend.fontsize'] = fontsize
matplotlib.rcParams['font.size'] = fontsize - 2
matplotlib.rcParams['font.family'] = ['sans-serif']
matplotlib.rcParams['font.sans-serif'] = ['STIXGeneral']
matplotlib.rcParams['text.usetex'] = False
matplotlib.rcParams['svg.fonttype'] = 'none'

legends={'qiskit_level3': 'Qiskit (level 3)',
         'rpo_level3': 'Qiskit with RPO (level 3)',
         'qiskit_level2': 'Qiskit (level 2)'}

def median_cell(data, column):
    as_list = [l.strip('][').split(', ') for l in data[column]]
    r = [map(float, l) for l in as_list]
    data[column + '_median'] = [median([i for i in l]) for l in r]
