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




#Import Qiskit classes
import qiskit
from qiskit.providers.aer.noise import NoiseModel
from qiskit import QuantumRegister, QuantumCircuit, ClassicalRegister
from qiskit.providers.aer.noise.errors.standard_errors import depolarizing_error, thermal_relaxation_error

#Import the qv function
import qiskit.ignis.verification.quantum_volume as qv
import numpy as np

import math



def quantumvolume(nbits=6, measure=True):
    """
        This is a nbit quantum volume circuit
        reference: https://qiskit.org/textbook/ch-quantum-hardware/measuring-quantum-volume.html
    """
    qubit_lists = [list(range(0, nbits))]
    qv_circs, qv_circs_nomeas = qv.qv_circuits(qubit_lists, 1)
    if measure is True:
        return qv_circs[0][0]
    else:
        return qv_circs_nomeas[0][0]


def circuits():
    for n_qubits in range(2, 27, 4):
        yield quantumvolume(n_qubits)
