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

"""Test the ConstantsStateOptimization pass"""

import unittest
from collections import defaultdict

from qiskit import QuantumRegister, QuantumCircuit
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import Unroller
from qiskit.extensions import HGate, ZGate, RYGate, SwapGate
from qiskit.compiler import transpile
from qiskit.test import QiskitTestCase
from qiskit.test.mock import FakeRueschlikon
from purestate import ConstantsStateOptimization, ASwapGate


class TestControlOnConstZero(QiskitTestCase):
    """Control on |0>"""

    def test_control_zero_cx_swap(self):
        """Swap(|0>, |1>); CX(|1>, |0>)
         |0> --X--X--       |0> -X--- |1>
               |  |     =>
         |1> --X--.--       |1> -X--- |0>
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.x(qr[1])
        circuit.swap(qr[0], qr[1])
        circuit.cx(qr[1], qr[0])

        expected = QuantumCircuit(qr)
        expected.x(qr[1])
        expected.x(qr)

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '1', qr[1]: '0'})
        self.assertEqual(expected, result)

    def test_custom(self):
        """Control on |0> of a custom gate
           ---ghz--          ------
               |      =>
         |0> --.---       |0> -----
         """
        qr = QuantumRegister(4, 'qr')
        ghz_circuit = QuantumCircuit(3, name='ghz')
        ghz_circuit.h(0)
        ghz_circuit.cx(0, 1)
        ghz_circuit.cx(1, 2)
        ghz = ghz_circuit.to_gate()
        cghz = ghz.control(1)
        circuit = QuantumCircuit(qr)
        circuit.append(cghz, [3, 1, 0, 2])

        expected = QuantumCircuit(qr)

        passmanager = PassManager()
        passmanager.append(ConstantsStateOptimization())
        result = passmanager.run(circuit)

        self.assertEqual(expected, result)

    def test_control_one_cx_swap(self):
        """Control on |1> (target is |0>, with swap)
         |0> --X--.--       |0> --X--- |1>
               |  |     =>
         |1> --X--X--       |1> -X--X- |1>
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.x(qr[1])
        circuit.swap(qr[0], qr[1])
        circuit.cx(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.x(qr[1])
        expected.x(qr)
        expected.x(qr[1])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '1', qr[1]: '1'})
        self.assertEqual(expected, result)

    def test_control_custom(self):
        """Control on |1> of a custom gate
           -/3--ghz--       -/3--ghz---
                 |      =>
         |1> ----.---       |1> -------
         """
        qr = QuantumRegister(4, 'qr')
        ghz_circuit = QuantumCircuit(3, name='ghz')
        ghz_circuit.h(0)
        ghz_circuit.cx(0, 1)
        ghz_circuit.cx(1, 2)
        ghz = ghz_circuit.to_gate()
        cghz = ghz.control(1)
        circuit = QuantumCircuit(qr)
        circuit.x(qr[3])
        circuit.append(cghz, [3, 1, 0, 2])

        expected = QuantumCircuit(qr)
        expected.x(qr[3])
        expected.append(ghz, [1, 0, 2])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: None,
                                                  qr[1]: None,
                                                  qr[2]: None,
                                                  qr[3]: '1'})
        self.assertEqual(expected, result)

    def test_reset(self):
        """Reset set back to zero constant
          -U-|0>-.--       -U-|0>---- |0>
                 |      =>
          -U-----X--       -U-------- (None)
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.u3(3.141, 1.571, 1.047, qr)
        circuit.reset(qr[0])
        circuit.cx(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.u3(3.141, 1.571, 1.047, qr)
        expected.reset(qr[0])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '0', qr[1]: None})
        self.assertEqual(expected, result)

    def test_control_other_cx(self):
        """Control on -X-Z-S-T-
         --X-Z-S-T-.--       -X-Z-S-T--
                   |      =>
             ------X---       ---X-----
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.x(qr[0])
        circuit.z(qr[0])
        circuit.s(qr[0])
        circuit.t(qr[0])
        circuit.cx(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.x(qr[0])
        expected.z(qr[0])
        expected.s(qr[0])
        expected.t(qr[0])
        expected.x(qr[1])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '1', qr[1]: '1'})
        self.assertEqual(expected, result)


class TestTargetOnPlus(QiskitTestCase):
    """Target on |+> removes CX"""

    def test_target_plus_cx_swap(self):
        """Target on |+> (with swap) removes CX
           |+> --X--.--      |+> --X--.-- None
                 |  |  =>          |  |
         |psi> --X--X--    |psi> -|0>-X-- |+>
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.u3(3.141, 1.571, 1.047, qr[1])
        circuit.h(qr[0])
        circuit.swap(qr[0], qr[1])
        circuit.cx(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.u3(3.141, 1.571, 1.047, qr[1])
        expected.h(qr[0])
        expected.append(ASwapGate(), [qr[1], qr[0]])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: None, qr[1]: '+'})
        self.assertEqual(expected, result)


class TestTargetOnMinus(QiskitTestCase):
    """Target on |-> removes CX"""

    def test_target_minus_cx_swap(self):
        """Target on |-> (with swap) removes CX
           |-> --X--.--         |-> ---X-Z- None
                 |  |    =>            |
         |psi> --X--X--       |psi> -Z-O--- |->
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.u3(3.141, 1.571, 1.047, qr[1])
        circuit.x(qr[0])
        circuit.h(qr[0])
        circuit.swap(qr[0], qr[1])
        circuit.cx(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.u3(3.141, 1.571, 1.047, qr[1])
        expected.x(qr[0])
        expected.h(qr[0])
        expected.z(qr[1])
        expected.append(ASwapGate(), [qr[1], qr[0]])
        expected.z(qr[0])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: None, qr[1]: '-'})
        self.assertEqual(expected, result)

    def test_target_minus_cx_idle(self):
        """Target on |->, control \psi>
          |u> -- . --      |u> --Z-- None
                 |     =>
          |-> ---X---      |-> -----  |->
        idle  -------          -----  |0>
         """
        qr = QuantumRegister(3, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.u3(3.141, 1.571, 1.047, qr[0])
        circuit.x(qr[1])
        circuit.h(qr[1])
        circuit.cx(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.u3(3.141, 1.571, 1.047, qr[0])
        expected.x(qr[1])
        expected.h(qr[1])
        expected.z(qr[0])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: None, qr[1]: '-', qr[2]: '0'})
        self.assertEqual(expected, result)


class TestMultiControlOnConst(QiskitTestCase):
    def test_control_zero_one(self):
        """Control on zero
         |0> --.-X-.--       --X--
               |   |    =>
         |x> --X---X--       --X--
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.u3(3.141, 1.571, 1.047, qr[1])
        circuit.cx(qr[0], qr[1])
        circuit.x(qr[0])
        circuit.cx(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.u3(3.141, 1.571, 1.047, qr[1])
        expected.x(qr[0])
        expected.x(qr[1])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '1', qr[1]: None})
        self.assertEqual(expected, result)

    def test_control_zero_one_swap(self):
        """Control on zero, swap, control on one.
         |0> --.-X-X-X--    -X-0-X- None
               |   | |   =>    |
         |x> --X---X-.--    -X-X--- 1
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.u3(3.141, 1.571, 1.047, qr[1])
        circuit.cx(qr[0], qr[1])
        circuit.x(qr[0])
        circuit.swap(qr[0], qr[1])
        circuit.cx(qr[1], qr[0])

        expected = QuantumCircuit(qr)
        expected.u3(3.141, 1.571, 1.047, qr[1])
        expected.x(qr[0])
        expected.x(qr[1])
        expected.append(ASwapGate(), [qr[0], qr[1]])
        expected.x(qr[0])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(expected, result)
        self.assertEqual(pass_.wire_state._dict, {qr[0]: None, qr[1]: '1'})


class TestToffoli(QiskitTestCase):

    def test_closed_open_psi_one(self):
        """Closed-Open Controlled H on psi-one
         |psi> -- . --       ---- None
                  |
           |1> -- o --   =>  ---- |1>
                  |
           |0> ---H---       ---- |0>
         """
        qr = QuantumRegister(3, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.u3(3.141, 1.571, 1.047, qr[0])
        circuit.x(qr[1])
        circuit.append(HGate().control(2, ctrl_state='01'), [qr[0], qr[1], qr[2]])

        expected = QuantumCircuit(qr)
        expected.u3(3.141, 1.571, 1.047, qr[0])
        expected.x(qr[1])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: None, qr[1]: '1', qr[2]: '0'})
        self.assertEqual(expected, result)

    def test_closed_open_psi_zero(self):
        """Closed-Open Control on psi-zero
         |psi> -- . --       ---.--- None
                  |             |
           |0> -- o --   =>  ---|--- |0>
                  |             |
               ---H---       ---H--- None
         """
        qr = QuantumRegister(3, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.u3(3.141, 1.571, 1.047, qr[0])
        circuit.append(HGate().control(2, ctrl_state='01'), [qr[0], qr[1], qr[2]])

        expected = QuantumCircuit(qr)
        expected.u3(3.141, 1.571, 1.047, qr[0])
        expected.append(HGate().control(1, ctrl_state='1'), [qr[0], qr[2]])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: None, qr[1]: '0', qr[2]: None})
        self.assertEqual(expected, result)

    def test_open_closed_psi_phi_minus(self):
        """Open-Closed Control on psi-phi-minus
         |psi> -- o --       ---o--- None
                  |             |
         |phi> -- . --   =>  ---Z--- None
                  |
           |-> ---X---       ------- |->
         """
        qr = QuantumRegister(3, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.u3(3.141, 1.571, 1.047, qr[0])
        circuit.u3(3.141, 1.571, 1.047, qr[1])
        circuit.x(qr[2])
        circuit.h(qr[2])
        circuit.append(HGate().control(2, ctrl_state='10'), [qr[0], qr[1], qr[2]])

        expected = QuantumCircuit(qr)
        expected.u3(3.141, 1.571, 1.047, qr[0])
        expected.u3(3.141, 1.571, 1.047, qr[1])
        expected.x(qr[2])
        expected.h(qr[2])
        expected.append(ZGate().control(1, ctrl_state='0'), [qr[0], qr[1]])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: None, qr[1]: None, qr[2]: '-'})
        self.assertEqual(expected, result)

    def test_closed_open_psi_phi_minus(self):
        """Closed-Open Control on psi-phi-minus
         |psi> -- . --       ---Z--- None
                  |             |
         |phi> -- o --   =>  ---o--- None
                  |
           |-> ---X---       ------- |->
         """
        qr = QuantumRegister(3, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.u3(3.141, 1.571, 1.047, qr[0])
        circuit.u3(3.141, 1.571, 1.047, qr[1])
        circuit.x(qr[2])
        circuit.h(qr[2])
        circuit.append(HGate().control(2, ctrl_state='01'), [qr[0], qr[1], qr[2]])

        expected = QuantumCircuit(qr)
        expected.u3(3.141, 1.571, 1.047, qr[0])
        expected.u3(3.141, 1.571, 1.047, qr[1])
        expected.x(qr[2])
        expected.h(qr[2])
        expected.append(ZGate().control(1, ctrl_state='0'), [qr[1], qr[0]])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: None, qr[1]: None, qr[2]: '-'})
        self.assertEqual(expected, result)




class TestSwap(QiskitTestCase):
    """ Constant relationship on Swap(top, bot) Table 2 of the paper"""

    def test_none_none(self):
        """Swap(None, None), do not change
         |U> --X-- None
               |
         |U> --X-- None
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.u3(3.141, 1.571, 1.047, qr)
        circuit.swap(qr[0], qr[1])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: None, qr[1]: None})
        self.assertEqual(circuit, result)

    def test_zero_none(self):
        """Swap(0, None) -> ASwap(0, 1) [None, 0]
           |0> --X--       --O-- None
                 |     =>    |
         |psi> --X--       --X-- |0>
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.u3(3.141, 1.571, 1.047, qr[1])
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.u3(3.141, 1.571, 1.047, qr[1])
        expected.append(ASwapGate(), [qr[0], qr[1]])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: None, qr[1]: '0'})
        self.assertEqual(expected, result)

    def test_one_none(self):
        """Swap(1, None) -> X(1);ASwap(0, 1) [None, 1]
           |1> --X--       ---O-- None
                 |     =>     |
         |psi> --X--       -X-X-- |1>
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.x(qr[0])
        circuit.u3(3.141, 1.571, 1.047, qr[1])
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.x(qr[0])
        expected.u3(3.141, 1.571, 1.047, qr[1])
        expected.x(qr[1])
        expected.append(ASwapGate(), [qr[0], qr[1]])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: None, qr[1]: '1'})
        self.assertEqual(expected, result)

    def test_plus_none(self):
        """Swap(+, None) -> ASwap(0, 1) [None, +]
           |+> --X--       --X-- None
                 |     =>    |
         |psi> --X--       --O-- |+>
        """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.u3(3.141, 1.571, 1.047, qr[1])
        circuit.h(qr[0])
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.u3(3.141, 1.571, 1.047, qr[1])
        expected.h(qr[0])
        expected.append(ASwapGate(), [qr[1], qr[0]])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: None, qr[1]: '+'})
        self.assertEqual(expected, result)

    def test_minus_none(self):
        """Swap(-, None) -> Z(1);ASwap(1, 0) [None, -]
           |-> --X--       ---X-- None
                 |     =>     |
         |psi> --X--       -X-O-- |->
        """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.u3(3.141, 1.571, 1.047, qr[1])
        circuit.x(qr[0])
        circuit.h(qr[0])
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.u3(3.141, 1.571, 1.047, qr[1])
        expected.x(qr[0])
        expected.h(qr[0])
        expected.z(qr[1])
        expected.append(ASwapGate(), [qr[1], qr[0]])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: None, qr[1]: '-'})
        self.assertEqual(expected, result)

    def test_none_zero(self):
        """Swap(None, 0) -> ASwap(1, 0) [0, None]
         |psi> --X--       --X-- 0
                 |     =>    |
           |0> --X--       --O-- None
        """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.u3(3.141, 1.571, 1.047, qr[0])
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.u3(3.141, 1.571, 1.047, qr[0])
        expected.append(ASwapGate(), [qr[1], qr[0]])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '0', qr[1]: None})
        self.assertEqual(expected, result)

    def test_zero_zero(self):
        """Swap(0, 0), can be removed
         |0> --X--
               |
         |0> --X--
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr)

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '0', qr[1]: '0'})
        self.assertEqual(expected, result)

    def test_one_zero(self):
        """Swap(1, 0) -> X(0); X(1) [0, 1]
           |1> --X--       ---X-- 0
                 |     =>
           |0> --X--       ---X-- 1
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.x(qr[0])
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.x(qr[0])
        expected.x(qr)

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '0', qr[1]: '1'})
        self.assertEqual(expected, result)

    def test_zero_none_idle(self):
        """Swap(0, None) -> ASwap(0, 1) [None, 0]
           |0> --X--       --O-- None
                 |     =>    |
         |psi> --X--       --X-- |0>
         idle  -----       ----- \0>
         """
        qr = QuantumRegister(3, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.u3(3.141, 1.571, 1.047, qr[1])
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.u3(3.141, 1.571, 1.047, qr[1])
        expected.append(ASwapGate(), [qr[0], qr[1]])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: None, qr[1]: '0', qr[2]: '0'})
        self.assertEqual(expected, result)

    def test_plus_zero(self):
        """Swap(+, 0) -> H(0); H(1) [0, +]
           |+> --X--       ---H-- 0
                 |     =>
           |0> --X--       ---H-- +
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.h(qr[0])
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.h(qr[0])
        expected.h(qr)

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '0', qr[1]: '+'})
        self.assertEqual(expected, result)

    def test_minus_zero(self):
        """Swap(-, 0) -> H(0); X(0); X(1); H(1) [0, -]
           |-> --X--       -H-X- 0
                 |     =>
           |0> --X--       -X-H- -
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.x(qr[0])
        circuit.h(qr[0])
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.x(qr[0])
        expected.h(qr[0])
        expected.h(qr[0])
        expected.x(qr[0])
        expected.x(qr[1])
        expected.h(qr[1])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '0', qr[1]: '-'})
        self.assertEqual(expected, result)

    def test_none_one(self):
        """Swap(None, 1) -> X(0);ASwap(1, 0) [1, None]
           |x> --X--       -X-X-- 1
                 |     =>     |
           |1> --X--       -x-O-- None
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.x(qr[1])
        circuit.u3(3.141, 1.571, 1.047, qr[0])
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.x(qr[1])
        expected.u3(3.141, 1.571, 1.047, qr[0])
        expected.x(qr[0])
        expected.append(ASwapGate(), [qr[1], qr[0]])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '1', qr[1]: None})
        self.assertEqual(expected, result)

    def test_zero_one(self):
        """Swap(0, 1) -> X(0); X(1) [1, None]
           |0> --X--       ---X-- 1
                 |     =>
           |1> --X--       ---X-- 0
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.x(qr[1])
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.x(qr[1])
        expected.x(qr)

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '1', qr[1]: '0'})
        self.assertEqual(expected, result)

    def test_one_one(self):
        """Swap(1, 1), can be removed
         |1> --X--
               |
         |1> --X--
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.x(qr)
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.x(qr)

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '1', qr[1]: '1'})
        self.assertEqual(expected, result)

    def test_plus_one(self):
        """Swap(+, 1) -> H(0); X(0); X(1); H(1) [1, +]
           |+> --X--       -H-X- 1
                 |     =>
           |1> --X--       -X-H- +
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.x(qr[1])
        circuit.h(qr[0])
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.x(qr[1])
        expected.h(qr[0])
        expected.h(qr[0])
        expected.x(qr[0])
        expected.x(qr[1])
        expected.h(qr[1])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '1', qr[1]: '+'})
        self.assertEqual(expected, result)

    def test_minus_one(self):
        """Swap(-, 1) -> H(0); H(1) [1, -]
           |-> --X--       --H-- 1
                 |     =>
           |1> --X--       --H-- -
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.x(qr)
        circuit.h(qr[0])
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.x(qr)
        expected.h(qr[0])
        expected.h(qr)

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '1', qr[1]: '-'})
        self.assertEqual(expected, result)

    def test_none_plus(self):
        """Swap(None, +) -> ASwap(0, 1) [+, None]
           |x> --X--       --O-- +
                 |     =>    |
           |+> --X--       --X-- None
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.u3(3.141, 1.571, 1.047, qr[0])
        circuit.h(qr[1])
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.u3(3.141, 1.571, 1.047, qr[0])
        expected.h(qr[1])
        expected.append(ASwapGate(), [qr[0], qr[1]])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '+', qr[1]: None})
        self.assertEqual(expected, result)

    def test_zero_plus(self):
        """Swap(0, +) -> H(0); H(1) [+, 0]
           |0> --X--       --H-- +
                 |     =>
           |+> --X--       --H-- 0
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.h(qr[1])
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.h(qr[1])
        expected.h(qr)

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '+', qr[1]: '0'})
        self.assertEqual(expected, result)

    def test_one_plus(self):
        """Swap(1, +) -> H(1); X(1); X(0); H(0) [+, 1]
           |1> --X--       -X-H- +
                 |     =>
           |+> --X--       -H-X- 1
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.x(qr[0])
        circuit.h(qr[1])
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.x(qr[0])
        expected.h(qr[1])
        expected.h(qr[1])
        expected.x(qr[1])
        expected.x(qr[0])
        expected.h(qr[0])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '+', qr[1]: '1'})
        self.assertEqual(expected, result)

    def test_plus_plus(self):
        """Swap(+, +), can be removed
         |+> --X--
               |
         |+> --X--
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.h(qr)
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.h(qr)

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '+', qr[1]: '+'})
        self.assertEqual(expected, result)

    def test_minus_plus(self):
        """Swap(-, +) -> Z(0); Z(1) [+, -]
           |-> --X--       ---Z-- |->
                 |     =>
           |+> --X--       ---Z-- |+>
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.x(qr[0])
        circuit.h(qr)
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.x(qr[0])
        expected.h(qr)
        expected.z(qr)

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '+', qr[1]: '-'})
        self.assertEqual(expected, result)

    def test_none_minus(self):
        """Swap(None, -) -> Z(0);ASwap(0, 1) [-, None]
           |x> --X--       ---X-- -
                 |     =>     |
           |-> --X--       -X-O-- None
        """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.u3(3.141, 1.571, 1.047, qr[0])
        circuit.x(qr[1])
        circuit.h(qr[1])
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.u3(3.141, 1.571, 1.047, qr[0])
        expected.x(qr[1])
        expected.h(qr[1])
        expected.z(qr[0])
        expected.append(ASwapGate(), [qr[0], qr[1]])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '-', qr[1]: None})
        self.assertEqual(expected, result)

    def test_zero_minus(self):
        """Swap(0, -) -> H(1); X(1); X(0); H(0) [-, 0]
           |0> --X--       -X-H- -
                 |     =>
           |-> --X--       -H-X- 0
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.x(qr[1])
        circuit.h(qr[1])
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.x(qr[1])
        expected.h(qr[1])
        expected.h(qr[1])
        expected.x(qr[1])
        expected.x(qr[0])
        expected.h(qr[0])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '-', qr[1]: '0'})
        self.assertEqual(expected, result)

    def test_one_minus(self):
        """Swap(1, -) -> H(0); H(1) [-, 1]
           |1> --X--       --H-- -
                 |     =>
           |-> --X--       --H-- 1
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.x(qr)
        circuit.h(qr[1])
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.x(qr)
        expected.h(qr[1])
        expected.h(qr)

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '-', qr[1]: '1'})
        self.assertEqual(expected, result)

    def test_plus_minus(self):
        """Swap(+, -) -> Z(0); Z(1) [-, +]
           |+> --X--       ---Z-- |->
                 |     =>
           |-> --X--       ---Z-- |+>
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.x(qr[1])
        circuit.h(qr)
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.x(qr[1])
        expected.h(qr)
        expected.z(qr)

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '-', qr[1]: '+'})
        self.assertEqual(expected, result)

    def test_minus_minus(self):
        """Swap(-, -), can be removed
         |-> --X--
               |
         |-> --X--
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.x(qr)
        circuit.h(qr)
        circuit.swap(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.x(qr)
        expected.h(qr)

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '-', qr[1]: '-'})
        self.assertEqual(expected, result)


class TestCnot(QiskitTestCase):
    """ Constant relationship on CX(control, target) Table 1 of the paper"""

    def test_none_none(self):
        """CX(None, None), do not change [None, None]
         |U> --.-- None
               |
         |U> --X-- None
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.u3(3.141, 1.571, 1.047, qr)
        circuit.cx(qr[0], qr[1])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: None, qr[1]: None})
        self.assertEqual(circuit, result)

    def test_zero_none(self):
        """CX(0, None) can be removed [0, None]
           |0> --.--       ---- |0>
                 |     =>
         |psi> --X--       ---- None
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.u3(3.141, 1.571, 1.047, qr[1])
        circuit.cx(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.u3(3.141, 1.571, 1.047, qr[1])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '0', qr[1]: None})
        self.assertEqual(expected, result)

    def test_one_none(self):
        """CX(1, None) -> X(1) [1, None]
           |1> --.--       ----- None
                 |     =>
         |psi> --X--       --X-- |1>
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.x(qr[0])
        circuit.u3(3.141, 1.571, 1.047, qr[1])
        circuit.cx(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.x(qr[0])
        expected.u3(3.141, 1.571, 1.047, qr[1])
        expected.x(qr[1])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '1', qr[1]: None})
        self.assertEqual(expected, result)

    def test_plus_none(self):
        """CX(+, None) does not change [None, None]
           |+> --.--
                 |
         |psi> --X--
        """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.u3(3.141, 1.571, 1.047, qr[1])
        circuit.h(qr[0])
        circuit.cx(qr[0], qr[1])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: None, qr[1]: None})
        self.assertEqual(circuit, result)

    def test_minus_none(self):
        """CX(-, None) does not change [None, None]
           |-> --.--
                 |
         |psi> --X--
        """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.u3(3.141, 1.571, 1.047, qr[1])
        circuit.x(qr[0])
        circuit.h(qr[0])
        circuit.cx(qr[0], qr[1])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: None, qr[1]: None})
        self.assertEqual(circuit, result)

    def test_none_zero(self):
        """CX(None, 0) does not change [None, None]
         |psi> --.--
                 |
           |0> --X--
        """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.u3(3.141, 1.571, 1.047, qr[0])
        circuit.cx(qr[0], qr[1])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: None, qr[1]: None})
        self.assertEqual(circuit, result)

    def test_zero_zero(self):
        """CX(0, 0), can be removed [0, 0]
         |0> --.--
               |
         |0> --X--
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.cx(qr[0], qr[1])

        expected = QuantumCircuit(qr)

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '0', qr[1]: '0'})
        self.assertEqual(expected, result)

    def test_one_zero(self):
        """CX(1, 0) -> X(1) [1, 1]
           |1> --.--       ------ 1
                 |     =>
           |0> --X--       ---X-- 1
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.x(qr[0])
        circuit.cx(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.x(qr[0])
        expected.x(qr[1])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '1', qr[1]: '1'})
        self.assertEqual(expected, result)

    def test_plus_zero(self):
        """CX(+, 0) does not change [None, None]
           |+> --.--
                 |
           |0> --X--
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.h(qr[0])
        circuit.cx(qr[0], qr[1])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: None, qr[1]: None})
        self.assertEqual(circuit, result)

    def test_minus_zero(self):
        """CX(-, 0) does not change [None, None]
           |-> --.--
                 |
           |0> --X--
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.x(qr[0])
        circuit.h(qr[0])
        circuit.cx(qr[0], qr[1])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: None, qr[1]: None})
        self.assertEqual(circuit, result)

    def test_none_one(self):
        """CX(None, 1) does not change [None, None]
           |x> --.--
                 |
           |1> --X--
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.x(qr[1])
        circuit.u3(3.141, 1.571, 1.047, qr[0])
        circuit.cx(qr[0], qr[1])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: None, qr[1]: None})
        self.assertEqual(circuit, result)

    def test_zero_one(self):
        """CX(0, 1), can be removed [0, 1]
           |0> --.--
                 |
           |1> --X--
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.x(qr[1])
        circuit.cx(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.x(qr[1])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '0', qr[1]: '1'})
        self.assertEqual(expected, result)

    def test_one_one(self):
        """CX(1, 1) -> X(1) [1, 0]
           |1> --.--       ------ 1
                 |     =>
           |1> --X--       ---X-- 0
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.x(qr)
        circuit.cx(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.x(qr)
        expected.x(qr[1])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '1', qr[1]: '0'})
        self.assertEqual(expected, result)

    def test_plus_one(self):
        """CX(+, 1) does not change [None, None]
           |+> --.--
                 |
           |1> --X--
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.x(qr[1])
        circuit.h(qr[0])
        circuit.cx(qr[0], qr[1])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: None, qr[1]: None})
        self.assertEqual(circuit, result)

    def test_minus_one(self):
        """CX(-, 1) does not change [None, None]
           |-> --.--
                 |
           |1> --X--
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.x(qr)
        circuit.h(qr[0])
        circuit.cx(qr[0], qr[1])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: None, qr[1]: None})
        self.assertEqual(circuit, result)

    def test_none_plus(self):
        """CX(None, +), can be removed [None, +]
           |x> --.--
                 |
           |+> --X--
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.u3(3.141, 1.571, 1.047, qr[0])
        circuit.h(qr[1])
        circuit.cx(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.u3(3.141, 1.571, 1.047, qr[0])
        expected.h(qr[1])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: None, qr[1]: '+'})
        self.assertEqual(expected, result)

    def test_zero_plus(self):
        """CX(0, +), can be removed [0, +]
           |0> --.--
                 |
           |+> --X--
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.h(qr[1])
        circuit.cx(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.h(qr[1])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '0', qr[1]: '+'})
        self.assertEqual(expected, result)

    def test_one_plus(self):
        """CX(1, +), can be removed [1, +]
           |1> --.--
                 |
           |+> --X--
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.x(qr[0])
        circuit.h(qr[1])
        circuit.cx(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.x(qr[0])
        expected.h(qr[1])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '1', qr[1]: '+'})
        self.assertEqual(expected, result)

    def test_plus_plus(self):
        """CX(+, +), can be removed [+, +]
         |+> --.--
               |
         |+> --X--
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.h(qr)
        circuit.cx(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.h(qr)

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '+', qr[1]: '+'})
        self.assertEqual(expected, result)

    def test_minus_plus(self):
        """CX(-, +), can be removed [-, +]
           |-> --.--
                 |
           |+> --X--
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.x(qr[0])
        circuit.h(qr)
        circuit.cx(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.x(qr[0])
        expected.h(qr)

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '-', qr[1]: '+'})
        self.assertEqual(expected, result)

    def test_none_minus(self):
        """CX(None, -) -> Z(0) [None, -]
           |x> --.--       --Z--
                 |     =>
           |-> --X--       -----
        """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.u3(3.141, 1.571, 1.047, qr[0])
        circuit.x(qr[1])
        circuit.h(qr[1])
        circuit.cx(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.u3(3.141, 1.571, 1.047, qr[0])
        expected.x(qr[1])
        expected.h(qr[1])
        expected.z(qr[0])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: None, qr[1]: '-'})
        self.assertEqual(expected, result)

    def test_zero_minus(self):
        """CX(0, -), can be removed [0, -]
           |0> --.--
                 |
           |-> --X--
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.x(qr[1])
        circuit.h(qr[1])
        circuit.cx(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.x(qr[1])
        expected.h(qr[1])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '0', qr[1]: '-'})
        self.assertEqual(expected, result)

    def test_one_minus(self):
        """CX(1, -), can be removed [1, -]
           |1> --.--
                 |
           |-> --X--
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.x(qr)
        circuit.h(qr[1])
        circuit.cx(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.x(qr)
        expected.h(qr[1])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '1', qr[1]: '-'})
        self.assertEqual(expected, result)

    def test_plus_minus(self):
        """CX(+, -) -> Z(0) [-, -]
           |+> --.--       --Z-- |->
                 |     =>
           |-> --X--       ----- |->
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.x(qr[1])
        circuit.h(qr)
        circuit.cx(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.x(qr[1])
        expected.h(qr)
        expected.z(qr[0])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '-', qr[1]: '-'})
        self.assertEqual(expected, result)

    def test_minus_minus(self):
        """CX(-, -) -> Z(0) [+, -]
           |-> --.--       --Z-- |+>
                 |     =>
           |-> --X--       ----- |->
         """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.x(qr)
        circuit.h(qr)
        circuit.cx(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.x(qr)
        expected.h(qr)
        expected.z(qr[0])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '+', qr[1]: '-'})
        self.assertEqual(expected, result)


class TestMultiRegisters(QiskitTestCase):
    def assertEqualWithIdle(self, result, expected):
        self.assertTrue(all(item in result.items() for item in expected.items()))

    def test_control_zero_one(self):
        """Control on zero
         qr1_1: |0> --.-X-.--       --X--
                      |   |    =>
         qr2_0: |x> --X---X--       --X--
         """
        qr1 = QuantumRegister(2, 'qr1')
        qr2 = QuantumRegister(2, 'qr2')

        circuit = QuantumCircuit(qr1, qr2)
        circuit.u3(3.141, 1.571, 1.047, qr2[0])
        circuit.cx(qr1[1], qr2[0])
        circuit.x(qr1[1])
        circuit.cx(qr1[1], qr2[0])

        expected = QuantumCircuit(qr1, qr2)
        expected.u3(3.141, 1.571, 1.047, qr2[0])
        expected.x(qr1[1])
        expected.x(qr2[0])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqualWithIdle(pass_.wire_state._dict, {qr1[1]: '1', qr2[0]: None})
        self.assertEqual(expected, result)

    def test_plus_minus(self):
        """Swap(+, -) -> Z(0); Z(1) [-, +]
          qr1_1: |+> --X--       ---Z-- |->
                       |     =>
          qr2_0: |-> --X--       ---Z-- |+>
         """
        qr1 = QuantumRegister(2, 'qr1')
        qr2 = QuantumRegister(2, 'qr2')

        circuit = QuantumCircuit(qr1, qr2)
        circuit.x(qr2[0])
        circuit.h(qr2[0])
        circuit.h(qr1[1])
        circuit.swap(qr1[1], qr2[0])

        expected = QuantumCircuit(qr1, qr2)
        expected.x(qr2[0])
        expected.h(qr2[0])
        expected.h(qr1[1])
        expected.z(qr2[0])
        expected.z(qr1[1])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqualWithIdle(pass_.wire_state._dict, {qr1[1]: '-', qr2[0]: '+'})
        self.assertEqual(expected, result)



class TestCSwap(QiskitTestCase):
    def test_zero_zero_zero(self):
        qr = QuantumRegister(3, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.cswap(2, 0, 1)

        expected = QuantumCircuit(qr)

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = transpile(circuit, pass_manager=passmanager)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '0', qr[1]: '0', qr[2]: '0'})
        self.assertEqual(expected, result)

    def test_cswap_is_unrolled_correctly(self):
        """
        See: https://github.com/Qiskit/qiskit-terra/issues/4032
        """
        circuit = QuantumCircuit(3)
        circuit.u3(5.3906, 5.3234, 3.918, 0)
        circuit.u3(5.3906, 5.3234, 3.918, 1)
        circuit.u3(5.3906, 5.3234, 3.918, 2)
        circuit.append(SwapGate().control(1), [2, 0, 1])

        expected = QuantumCircuit(3)
        expected.u3(5.3906, 5.3234, 3.918, 0)
        expected.u3(5.3906, 5.3234, 3.918, 1)
        expected.u3(5.3906, 5.3234, 3.918, 2)
        expected.cx(1, 0)
        expected.ccx(2, 0, 1)
        expected.cx(1, 0)

        passmanager = PassManager([ConstantsStateOptimization(), Unroller(['cx', 'u3', 'ccx'])])
        result = passmanager.run(circuit)

        self.assertEqual(expected, result)


class TestBugs(QiskitTestCase):
    def test_bug001(self):
        qr = QuantumRegister(2, 'qr')

        circuit = QuantumCircuit(qr)
        circuit.x(qr[1])
        circuit.h(qr)
        circuit.cx(qr[0], qr[1])

        expected = QuantumCircuit(qr)
        expected.x(qr[1])
        expected.h(qr)
        expected.z(qr[0])

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '-', qr[1]: '-'})
        self.assertEqual(expected, result)

    def test_bug002(self):
        circuit = QuantumCircuit(3)
        circuit.x(0)
        circuit.h(1)
        circuit.x(2)
        circuit.h(2)
        circuit.ccx(0, 1, 2)
        circuit.h(1)

        expected = QuantumCircuit(3)
        expected.x(0)
        expected.h(1)
        expected.z(1)
        expected.h(1)
        expected.x(2)
        expected.h(2)

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(expected, result)

    def test_bug003(self):
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

        expected = QuantumCircuit(3)
        expected.z(0)
        expected.h(1)
        expected.u3(5.3906, 5.3234, 3.918, 2)
        expected.t(1)
        expected.append(ASwapGate(), [0, 2])
        expected.ry(4.9042, 0)
        expected.u3(6.014, 0.88185, 5.4669, 1)

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(expected, result)

    def test_bug004(self):
        qr = QuantumRegister(4, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.ccx(qr[1], qr[3], qr[0])

        expected = QuantumCircuit(qr)

        passmanager = PassManager()
        pass_ = ConstantsStateOptimization()
        passmanager.append(pass_)
        result = passmanager.run(circuit)

        self.assertEqual(pass_.wire_state._dict, {qr[0]: '0', qr[1]: '0', qr[2]: '0', qr[3]: '0'})
        self.assertEqual(expected, result)

if __name__ == '__main__':
    unittest.main()
