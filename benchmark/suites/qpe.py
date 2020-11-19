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


def QPE(nbits=5, expected_output=None, measure=True):
    """This is a nbit QPE algorithm that transforms a superpositon state to
       an expected classical state "expected_output"
    """
    if expected_output is None:
        expected_output = 2 ** nbits - 1

    qr = QuantumRegister(nbits + 1, 'qr')
    cr = ClassicalRegister(nbits, 'cr')
    circuit = QuantumCircuit(qr, cr)

    circuit.x(qr[nbits])
    # n-qubit input state for QPE that produces classical output.
    for j in range(nbits):
        circuit.h(j)
        circuit.cu1(np.mod(-expected_output * np.pi / float(2 ** (j)), 2*np.pi), j, nbits)
    # n-qubit QPE circuit
    for j in range(nbits):
        for k in range(j):
            circuit.cu1(np.pi / float(2 ** (j - k)), qr[j], qr[k])
        circuit.h(qr[j])

    if measure is True:
        circuit.measure(qr[0:nbits], cr[0:nbits])
    return circuit


def circuits():
    for n_qubits in range(3, 15, 2):
        yield QPE(n_qubits)
