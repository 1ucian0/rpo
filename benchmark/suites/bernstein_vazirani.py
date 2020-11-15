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

import numpy as np
import math

def bernstein_vazirani(nbits = 4, expected_output = 2**4 - 1, measure=True):
    """
        This is a n bit bernstein vazirani algorithm with one ancilla qubit
        The hidden oracle value is initialized to 11, which represents the binary string '1011'
        The CNOTs in the hidden oracle of bernstein vazirani algorithm should be optimized by the ControlOnConstant pass,
        The CNOTs have target bits in |-> state, so they should be optimized into Z gates.
        reference:https://arxiv.org/pdf/1804.03719.pdf
    """
    qr = QuantumRegister(nbits + 1, 'qr')
    circuit = QuantumCircuit(qr)
    for i in range(0, nbits):
        circuit.h(qr[i])
    circuit.x(qr[nbits])
    circuit.h(qr[nbits])
    # Apply the inner-product oracle
    for j in range(nbits):
        if (expected_output & (1 << j)):
            circuit.cx(qr[j], qr[nbits])
    for i in range(0, nbits):
        circuit.h(qr[i])
    if measure is True:
        circuit.measure_all()
    return circuit
