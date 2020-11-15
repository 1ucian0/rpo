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

from os import path
from qiskit import QuantumCircuit

QASMDIR = path.dirname(path.abspath(__file__))


def circuits():
    for n_qubits in range(2, 15, 2):
        filename = "VQE_" + str(n_qubits) + "node.qasm"
        qc = QuantumCircuit.from_qasm_file(path.join(QASMDIR, filename))
        yield qc
