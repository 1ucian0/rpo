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

from qiskit.test import QiskitTestCase
from qiskit.compiler import transpile
from qiskit import execute, Aer, QuantumCircuit
from qiskit.circuit.random import random_circuit

from passmanager import level_3_with_contant_pure
from qiskit.transpiler import PassManagerConfig
from qiskit.transpiler.coupling import CouplingMap
from qiskit.extensions import RYGate
from ddt import ddt, data, unpack
from itertools import product


class ExecutePassManager(QiskitTestCase):
    pm_conf = PassManagerConfig(
        initial_layout=None,
        basis_gates=['u1', 'u2', 'u3', 'cx', 'id'],
        coupling_map=CouplingMap([(0, 1), (1, 2), (2, 3), (3, 4)]),
        backend_properties=None,
        seed_transpiler=1)
    backend = Aer.get_backend('qasm_simulator')
    shots = 2048

    def assertEqualCounts(self, result, expected):
        result_count = result.get_counts()
        expected_count = expected.get_counts()
        for key in set(result_count.keys()).union(expected_count.keys()):
            with self.subTest(key=key):
                diff = abs(result_count.get(key, 0) - expected_count.get(key, 0))
                self.assertLess(diff / self.shots * 100, 2.5)

    def execute(self, circuit):
        return execute(circuit, self.backend,
                       basis_gates=['u1', 'u2', 'u3', 'id', 'cx'],
                       seed_simulator=0,
                       seed_transpiler=0, shots=self.shots)


@ddt
class TestExecutePassManager(ExecutePassManager):
    @data(*[i for i in product(range(2, 6), range(1, 15))])
    @unpack
    def test_execute(self, n_qubits, depth):
        circuit = random_circuit(n_qubits, depth, reset=True, measure=True, seed=0)

        transpiled = transpile(circuit, pass_manager=level_3_with_contant_pure(self.pm_conf))

        expected = self.execute(circuit).result()
        result = self.execute(transpiled).result()

        self.assertEqualCounts(result, expected)


class TestExecuteSpecialCases(ExecutePassManager):
    def test_case_01(self):
        """
        q_0: |top>────■──
                    ┌─┴─┐
        q_1: |->────┤ X ├
                    └───┘
        """
        circuit = QuantumCircuit(2)
        circuit.u3(3.141, 1.571, 1.047, 0)
        circuit.x(1)
        circuit.h(1)
        circuit.cx(0, 1)
        circuit.measure_all()

        transpiled = transpile(circuit, pass_manager=level_3_with_contant_pure(self.pm_conf))

        expected = self.execute(circuit).result()
        result = self.execute(transpiled).result()

        self.assertEqualCounts(result, expected)

    def test_case_02(self):
        """
            q_0: |1>──■──
                      |
            q_1: |1>──■──
                    ┌─┴─┐
            q_2: |->┤ X ├
                    └───┘
        """
        circuit = QuantumCircuit(3)
        circuit.x(0)
        circuit.x(1)
        circuit.x(2)
        circuit.h(2)
        circuit.ccx(0, 1, 2)
        circuit.measure_all()

        transpiled = transpile(circuit, pass_manager=level_3_with_contant_pure(self.pm_conf))

        expected = self.execute(circuit).result()
        result = self.execute(transpiled).result()

        self.assertEqualCounts(result, expected)

    def test_case_03(self):
        """
        """
        circuit = QuantumCircuit(3)
        circuit.x(0)
        circuit.h(1)
        circuit.x(2)
        circuit.h(2)
        circuit.ccx(0, 1, 2)
        circuit.h(1)
        circuit.measure_all()

        transpiled = transpile(circuit, pass_manager=level_3_with_contant_pure(self.pm_conf))

        expected = self.execute(circuit).result()
        result = self.execute(transpiled).result()

        self.assertEqualCounts(result, expected)

    def test_case_04(self):
        circuit = random_circuit(n_qubits=5, depth=14, reset=True, measure=True, seed=0)

        transpiled = transpile(circuit, pass_manager=level_3_with_contant_pure(self.pm_conf))

        expected = self.execute(circuit).result()
        result = self.execute(transpiled).result()

        self.assertEqualCounts(result, expected)

    def test_case_05(self):
        circuit = QuantumCircuit(3)
        circuit.z(0)
        circuit.h(1)
        circuit.u3(5.3906, 5.3234, 3.918, 2)
        circuit.t(1)
        circuit.swap(0, 2)
        circuit.cswap(2, 1, 0)
        circuit.append(RYGate(0.12704).control(1), [2, 0])
        circuit.ry(4.9042, 0)
        circuit.u3(6.014, 0.88185, 5.4669, 1)
        circuit.measure_all()

        transpiled = transpile(circuit, pass_manager=level_3_with_contant_pure(self.pm_conf))

        expected = self.execute(circuit).result()
        result = self.execute(transpiled).result()

        self.assertEqualCounts(result, expected)

    def test_case_06(self):
        circuit = QuantumCircuit(4)
        circuit.u3(5.3906, 5.3234, 3.918, 2)
        circuit.ccx(1, 3, 0)
        circuit.u1(4.9746, 1)
        circuit.cswap(0, 2, 3)
        circuit.cx(0, 1)
        circuit.append(RYGate(0.12704).control(1), [2, 3])
        circuit.measure_all()

        transpiled = transpile(circuit, pass_manager=level_3_with_contant_pure(self.pm_conf))

        expected = self.execute(circuit).result()
        result = self.execute(transpiled).result()

        self.assertEqualCounts(result, expected)
