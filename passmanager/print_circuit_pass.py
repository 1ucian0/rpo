# -*- coding: utf-8 -*-

# This code is based on Qiskit. qiskit/transpiler/preset_passmanagers/level3.py
# (C) Copyright IBM 2017, 2018.
#
# Modified by Luciano Bello
# (C) Copyright Ji Liu and Luciano Bello, 2020.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.


from qiskit.transpiler.basepasses import AnalysisPass
from qiskit.converters.dag_to_circuit import dag_to_circuit


class PrintCircuit(AnalysisPass):
    def run(self, dag):
        """prints if there is an improvement in depth and count_ops. Also the circuit"""
        # if self.property_set['depth']:
        #     print('depth', self.property_set['depth'] != dag.depth(), self.property_set['depth'], dag.depth())
        # self.property_set['depth'] = dag.depth()

        print(dag.count_ops())

        # print(dag_to_circuit(dag))
