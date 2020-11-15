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
from purestate import StateAnnotation

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


class TestAnnotation(PureStateTestCase):
    def test_empty_annotation(self):
        """Empty circuit with annotation
         |phi> --annotation----       |phi> --
                                  =>
         |phi>--------------        phi> --
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.u3(1.23, 2.34, 3.04, qr[0])
        circuit.u3(1.23, 2.34, 3.04, qr[1])
        circuit.swap(qr[0], qr[1])
        circuit.append(StateAnnotation(0.1, 0.2, 0.3), [qr[0]])

        expected = QuantumCircuit(qr)
        expected.u3(1.23, 2.34, 3.04, qr[0])
        expected.u3(1.23, 2.34, 3.04, qr[1])

        passmanager = PassManager()
        passmanager.append(PureStateOnU())
        result = passmanager.run(circuit)

        self.assertEqual(expected, result)


    def test_same_annotation_swap(self):
        """SWAP gate after same annotation should be removed
         |phi> --annotation------x-             |phi> --
                                |       =>
         |phi>---annotation----x-            |phi> --
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.append(StateAnnotation(0.1, 0.2, 0.3), [qr[0]])
        circuit.append(StateAnnotation(0.1, 0.2, 0.3), [qr[1]])
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr)

        passmanager = PassManager()
        passmanager.append(PureStateOnU())
        result = passmanager.run(circuit)

        self.assertEqual(expected, result)

    def test_two_annotation_swap(self):
        """SWAP gate after different annotation should be optimized
         |phi> --annotation------x-             |phi> --
                                |       =>
         |phi>---annotation----x-            |phi> --
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.append(StateAnnotation(0.1, 0.2, 0.3), [qr[0]])
        circuit.append(StateAnnotation(0.4, 0.5, 0.6), [qr[1]])
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.u3(0.4, 0.5, 0.6, qr[0])
        expected.u3(0.1, 0.2, 0.3, qr[1])

        passmanager = PassManager()
        passmanager.append(PureStateOnU())
        result = passmanager.run(circuit)

        print(expected)
        print(result)
        self.assertEqual(expected, result)



if __name__ == '__main__':
    unittest.main()
