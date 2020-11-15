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


def hidden_shift(nbits=6, expected_output=None, measure=True):
    """
        Nbits should always be even.
        This is a nbit hiddenshift algorithm that finds the hidden shift string "s" for
        which f(x) = f(x + s) reference: https://www.pnas.org/content/114/13/3305.full
    """
    if expected_output is None:
        expected_output = 2 ** nbits - 1

    qr = QuantumRegister(nbits, 'qr')

    circuit = QuantumCircuit(qr, cr)
    for i in range(0, nbits):
        circuit.h(qr[i])
    for i in range(0, nbits):
        if (expected_output & (1 << i)):
            circuit.x(qr[i])
    for i in range(0, nbits):
        if i % 2 == 0:
            circuit.cz(qr[i], qr[i + 1])
    for i in range(0, nbits):
        if (expected_output & (1 << i)):
            circuit.x(qr[i])
    for i in range(0, nbits):
        circuit.h(qr[i])
    for i in range(0, nbits):
        if i % 2 == 0:
            circuit.cz(qr[i], qr[i + 1])
    for i in range(0, nbits):
        circuit.h(qr[i])
    if measure is True:
        circuit.measure_all()
    return circuit


def circuits():
    for n_qubits in range(2, 15, 2):
        yield hidden_shift(n_qubits)
