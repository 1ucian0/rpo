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

import matplotlib.pylab as plt
from benchmark.utils import legends
from qiskit.visualization import plot_histogram
from matplotlib.patches import Patch

results = {'almaden': {'qiskit_level3': {'111': 1089,
                                         '000': 655,
                                         '101': 621,
                                         '100': 550,
                                         '001': 960,
                                         '110': 699,
                                         '010': 1160,
                                         '011': 2458},
                       'rpo_level3': {'111': 2935,
                                      '000': 532,
                                      '101': 1138,
                                      '100': 746,
                                      '001': 683,
                                      '110': 1025,
                                      '010': 360,
                                      '011': 773}},
           'melbourne': {'qiskit_level3': {'000': 942,
                                           '111': 716,
                                           '001': 721,
                                           '101': 1166,
                                           '110': 1094,
                                           '011': 1117,
                                           '100': 1484,
                                           '010': 952},
                         'rpo_level3': {'000': 850,
                                        '111': 2094,
                                        '001': 780,
                                        '101': 1298,
                                        '110': 1107,
                                        '011': 755,
                                        '100': 601,
                                        '010': 707}},
           'rochester': {'qiskit_level3': {'110': 948,
                                           '111': 1740,
                                           '010': 593,
                                           '000': 865,
                                           '001': 1137,
                                           '100': 803,
                                           '011': 965,
                                           '101': 1141},
                         'rpo_level3': {'110': 1026,
                                        '111': 2658,
                                        '010': 531,
                                        '000': 637,
                                        '001': 583,
                                        '100': 716,
                                        '011': 1296,
                                        '101': 745}}
           }

for backend, result in results.items():
    fig, ax = plt.subplots()
    plot_histogram([result['qiskit_level3'], result['rpo_level3']], bar_labels=False,
                   ax=ax)

    patch_1 = Patch(label=legends['qiskit_level3'], facecolor='#648fff', hatch='///', fill=True)
    patch_2 = Patch(label=legends['rpo_level3'], facecolor='#dc267f', fill=True)
    ax.legend(handles=[patch_1, patch_2], loc='upper left')

    rects = ax.patches

    top2_heights = sorted([rect.get_height() for rect in rects])[-2:]
    for rect in rects:
        height = rect.get_height()
        if height in top2_heights:
            ax.text(rect.get_x()-rect.get_x()*0.03, 1.03*height, '%.2f' % height)
        if rect.get_facecolor()[0] < 0.5:
            rect.set_hatch('///')

    plt.savefig('qpe_histogram_%s.pdf' % backend)
