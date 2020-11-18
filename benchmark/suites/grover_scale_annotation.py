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


from qiskit import QuantumRegister, QuantumCircuit, ClassicalRegister
from purestate import StateAnnotation
import numpy as np
import math


def grover_annotation(nbits=15, iteration=None, measure=True):
    """
        This is a nbit Grover's algorithm that find (with probability close to 1) a specific item
        within a randomly ordered database of N items using O(√N) operations
        reference: https://ieeexplore.ieee.org/abstract/document/8622457
    """

    qr = QuantumRegister(nbits, 'qr')
    circuit = QuantumCircuit(qr)

    if iteration is None:
        iteration = int(round(np.pi / 4 * math.sqrt(2 ** nbits)))
    for i in range(0, iteration):
        # oracle
        for i in range(0, 8):
            circuit.h(i)
        circuit.mct(qr[0:8], qr[14], qr[8:14])
        for i in range(8, 14):
            circuit.append(StateAnnotation(0, 0, 0), [qr[i]])
        for i in range(0, 8):
            circuit.h(i)

        # Grover's diffusion operator
        for i in range(0, 8):
            circuit.h(i)
            circuit.x(i)
        circuit.mct(qr[0:8], qr[14], qr[8:14])
        for i in range(8, 14):
            circuit.append(StateAnnotation(0, 0, 0), [qr[i]])
        for i in range(0, 8):
            circuit.x(i)
            circuit.h(i)
    if measure is True:
        circuit.measure_all()
    return circuit


def circuits():
    for iteration in range(2, 16, 2):
        yield grover_annotation(15, iteration)
