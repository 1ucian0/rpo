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

"""Test the 2-CNOT-SWAP Gates (SWAPL and SWAPR)."""

import unittest

from qiskit import QuantumRegister, QuantumCircuit
from qiskit.transpiler.passes import Unroller
from qiskit.test import QiskitTestCase
from qiskit.converters import circuit_to_dag
from purestate import ASwapGate


class PureStateTestCase(QiskitTestCase):
    def assertEqualUnroll(self, basis, circuit, expected):
        """ Compares the dags after unrolling to basis """
        circuit_dag = circuit_to_dag(circuit)
        expected_dag = circuit_to_dag(expected)

        circuit_result = Unroller(basis).run(circuit_dag)
        expected_result = Unroller(basis).run(expected_dag)

        self.assertEqual(circuit_result, expected_result)


class TestSWAPL(PureStateTestCase):
    def test_decomposition(self):
        """Check SWAPL decomposition
         """
        qr = QuantumRegister(3, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.append(ASwapGate(), [qr[0], qr[2]])

        expected = QuantumCircuit(qr)
        expected.cx(qr[2], qr[0])
        expected.cx(qr[0], qr[2])

        self.assertEqualUnroll(['cx'], circuit, expected)


class TestSWAPR(PureStateTestCase):
    def test_decomposition(self):
        """Check SWAPR decomposition
         """
        qr = QuantumRegister(3, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.append(ASwapGate(), [qr[2], qr[0]])

        expected = QuantumCircuit(qr)
        expected.cx(qr[0], qr[2])
        expected.cx(qr[2], qr[0])

        self.assertEqualUnroll(['cx'], circuit, expected)


if __name__ == '__main__':
    unittest.main()
