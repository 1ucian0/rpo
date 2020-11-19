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

"""Test the ControlOnConstant pass"""

import unittest

from qiskit import QuantumRegister, QuantumCircuit
from qiskit.transpiler import PassManager
from qiskit.extensions import HGate
from qiskit.compiler import transpile
from qiskit.test import QiskitTestCase
from qiskit.test.mock import FakeRueschlikon
from purestate import PureStateOnU
from qiskit.transpiler.passes import Optimize1qGates
from qiskit.converters import circuit_to_dag
from qiskit.transpiler.passes import Unroller
from purestate import ASwapGate

import numpy as np


class PureStateTestCase(QiskitTestCase):
    def assertEqualUnroll(self, basis, circuit, expected, pass_=None):
        """ Compares the dags after unrolling to basis """
        passmanager = PassManager()
        unrollpass = Unroller(basis)
        if pass_ is not None:
            for passes in pass_:
                passmanager.append(passes)
        passmanager.append(unrollpass)
        circuit_result = passmanager.run(circuit)
        expected_result = passmanager.run(expected)
        self.assertEqual(circuit_result, expected_result)


class TestSWAPGates(PureStateTestCase):
    def test_same_const_swap(self):
        """Input states are the same, remove the swap gate
         |phi> --X----       |phi> --
                 |       =>
         |phi>--X----       |phi> --
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.u3(1.23, 2.34, 3.04, qr[0])
        circuit.u3(1.23, 2.34, 3.04, qr[1])
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.u3(1.23, 2.34, 3.04, qr[0])
        expected.u3(1.23, 2.34, 3.04, qr[1])

        passmanager = PassManager()
        passmanager.append(PureStateOnU())
        result = passmanager.run(circuit)

        self.assertEqual(expected, result)

    def test_two_unknown_swap(self):
        """Input states are the same, remove the swap gate
         |phi> --X----       |phi> --
                 |       =>
         |phi>--X----       |phi> --
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.reset(qr[0])
        circuit.reset(qr[1])
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.reset(qr[0])
        expected.reset(qr[1])
        expected.swap(qr[0], qr[1])

        passmanager = PassManager()
        passmanager.append(PureStateOnU())
        result = passmanager.run(circuit)

        self.assertEqual(expected, result)

    def test_two_const_swap(self):
        """Input states are the different pure states, replace the swap with two single qubit gates
         |phi> --X----       |phi> --U3--
                 |       =>
         |psi>--X----       |psi> --U3^--
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.u3(1.23, 3.34, 3.04, qr[0])
        circuit.u3(2.22, 1.67, 0.66, qr[1])
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.u3(2.22, 1.67, 0.66, qr[0])
        expected.u3(1.23, 3.34, 3.04, qr[1])

        passmanager = PassManager()
        passmanager.append(PureStateOnU())
        passmanager.append(Optimize1qGates())
        result = passmanager.run(circuit)

        self.assertEqual(expected, result)

    def test_two_const_swap2(self):
        """Input states are the different pure states, replace the swap with two single qubit gates
         |phi> --X----       |phi> --U3--
                 |       =>
         |psi> --X----       |psi> --U3^--
         """
        qr = QuantumRegister(4, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.u3(1.23, 3.34, 3.04, qr[0])
        circuit.u3(2.22, 1.67, 0.66, qr[1])
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.u3(2.22, 1.67, 0.66, qr[0])
        expected.u3(1.23, 3.34, 3.04, qr[1])

        passmanager = PassManager()
        passmanager.append(PureStateOnU())
        passmanager.append(Optimize1qGates())
        result = passmanager.run(circuit)

        self.assertEqual(expected, result)

    def test_two_const_swap3(self):
        """Input states are the different pure states, replace the swap with two single qubit gates
         |phi> --X----       |phi> --U3--
                 |       =>
         |psi>--X----       |psi> --U3^--
         """
        qr = QuantumRegister(4, 'qreg')
        qr2 = QuantumRegister(4, 'qreg2')
        circuit = QuantumCircuit(qr, qr2)
        circuit.u3(1.23, 3.34, 3.04, qr[0])
        circuit.u3(2.22, 1.67, 0.66, qr[1])
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr, qr2)
        expected.u3(2.22, 1.67, 0.66, qr[0])
        expected.u3(1.23, 3.34, 3.04, qr[1])

        passmanager = PassManager()
        passmanager.append(PureStateOnU())
        passmanager.append(Optimize1qGates())
        result = passmanager.run(circuit)

        self.assertEqual(expected, result)

    def test_two_const_swap4(self):
        """Input states are the different pure states, replace the swap with two single qubit gates
         |phi> --X----       |phi> --U3--
                 |       =>
         |psi>--X----       |psi> --U3^--
         """
        qr = QuantumRegister(4, 'qreg')
        qr2 = QuantumRegister(4, 'qreg2')
        circuit = QuantumCircuit(qr, qr2)
        circuit.u3(2.22, 1.67, 0.66, qr[1])
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr, qr2)
        expected.u3(2.22, 1.67, 0.66, qr[0])

        passmanager = PassManager()
        passmanager.append(PureStateOnU())
        passmanager.append(Optimize1qGates())
        result = passmanager.run(circuit)

        self.assertEqual(expected, result)

    def test_first_zero_swap(self):
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.reset(qr[1])
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.reset(qr[1])
        expected.cx(qr[1], qr[0])
        expected.cx(qr[0], qr[1])

        passmanager = PassManager()
        passmanager.append(PureStateOnU())
        result = passmanager.run(circuit)
        self.assertEqualUnroll(['cx'], result, expected)

    def test_second_zero_swap(self):
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.reset(qr[0])
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.reset(qr[0])
        expected.cx(qr[0], qr[1])
        expected.cx(qr[1], qr[0])

        passmanager = PassManager()
        passmanager.append(PureStateOnU())
        result = passmanager.run(circuit)
        self.assertEqualUnroll(['cx'], result, expected)

class TestASWAPGates(PureStateTestCase):
    def test_same_const_aswap(self):
        """Input states are the same, remove the swap gate
         |phi> --X----       |phi> --
                 |       =>
         |phi>--X----       |phi> --
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.u3(1.23, 2.34, 3.04, qr[0])
        circuit.u3(1.23, 2.34, 3.04, qr[1])
        circuit.append(ASwapGate(), [qr[1], qr[0]])

        expected = QuantumCircuit(qr)
        expected.u3(1.23, 2.34, 3.04, qr[0])
        expected.u3(1.23, 2.34, 3.04, qr[1])

        passmanager = PassManager()
        passmanager.append(PureStateOnU())
        result = passmanager.run(circuit)

        self.assertEqual(expected, result)

    def test_same_const_aswap_reverse(self):
        """Input states are the same, remove the swap gate
         |phi> --X----       |phi> --
                 |       =>
         |phi>--X----       |phi> --
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.u3(1.23, 2.34, 3.04, qr[0])
        circuit.u3(1.23, 2.34, 3.04, qr[1])
        circuit.append(ASwapGate(), [qr[0], qr[1]])

        expected = QuantumCircuit(qr)
        expected.u3(1.23, 2.34, 3.04, qr[0])
        expected.u3(1.23, 2.34, 3.04, qr[1])

        passmanager = PassManager()
        passmanager.append(PureStateOnU())
        result = passmanager.run(circuit)

        self.assertEqual(expected, result)

    def test_different_const_aswap(self):
        """Input states are the different pure states, replace the swap with two single qubit gates
         |phi> --X----       |phi> --U3--
                 |       =>
         |psi>--X----       |psi> --U3^--
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.u3(1.23, 3.34, 3.04, qr[0])
        circuit.u3(2.22, 1.67, 0.66, qr[1])
        circuit.append(ASwapGate(), [qr[1], qr[0]])

        expected = QuantumCircuit(qr)
        expected.u3(2.22, 1.67, 0.66, qr[0])
        expected.u3(1.23, 3.34, 3.04, qr[1])

        passmanager = PassManager()
        passmanager.append(PureStateOnU())
        passmanager.append(Optimize1qGates())
        result = passmanager.run(circuit)

        self.assertEqual(expected, result)

    def test_different_const_aswap_reverse(self):
        """Input states are the different pure states, replace the swap with two single qubit gates
         |phi> --X----       |phi> --U3--
                 |       =>
         |psi>--X----       |psi> --U3^--
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.u3(1.23, 3.34, 3.04, qr[0])
        circuit.u3(2.22, 1.67, 0.66, qr[1])
        circuit.append(ASwapGate(), [qr[0], qr[1]])

        expected = QuantumCircuit(qr)
        expected.u3(2.22, 1.67, 0.66, qr[0])
        expected.u3(1.23, 3.34, 3.04, qr[1])

        passmanager = PassManager()
        passmanager.append(PureStateOnU())
        passmanager.append(Optimize1qGates())
        result = passmanager.run(circuit)

        self.assertEqual(expected, result)

if __name__ == '__main__':
    unittest.main()
