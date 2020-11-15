# -*- coding: utf-8 -*-

# This code is based on Qiskit. qiskit/transpiler/preset_passmanagers/level3.py
# (C) Copyright IBM 2017, 2018.
#
# Modified by Luciano Bello
# (C) Copyright Ji Liu and Luciano Bello, 2020.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""
Based on qiskit/transpiler/preset_passmanagers/level3.py
Pass manager for optimization level 3, providing heavy optimization.
"""

from qiskit.transpiler.passmanager_config import PassManagerConfig
from qiskit.transpiler.passmanager import PassManager

from qiskit.transpiler.passes import Unroller
from qiskit.transpiler.passes import Unroll3qOrMore
from qiskit.transpiler.passes import CheckMap
from qiskit.transpiler.passes import CXDirection
from qiskit.transpiler.passes import SetLayout
from qiskit.transpiler.passes import CSPLayout
from qiskit.transpiler.passes import TrivialLayout
from qiskit.transpiler.passes import DenseLayout
from qiskit.transpiler.passes import NoiseAdaptiveLayout
from qiskit.transpiler.passes import BarrierBeforeFinalMeasurements
from qiskit.transpiler.passes import BasicSwap
from qiskit.transpiler.passes import LookaheadSwap
from qiskit.transpiler.passes import StochasticSwap
from qiskit.transpiler.passes import FullAncillaAllocation
from qiskit.transpiler.passes import EnlargeWithAncilla
from qiskit.transpiler.passes import FixedPoint
from qiskit.transpiler.passes import Depth
from qiskit.transpiler.passes import RemoveResetInZeroState
from qiskit.transpiler.passes import Optimize1qGates
from qiskit.transpiler.passes import CommutativeCancellation
from qiskit.transpiler.passes import OptimizeSwapBeforeMeasure
from qiskit.transpiler.passes import RemoveDiagonalGatesBeforeMeasure
from qiskit.transpiler.passes import Collect2qBlocks
from qiskit.transpiler.passes import ConsolidateBlocks
from qiskit.transpiler.passes import ApplyLayout
from qiskit.transpiler.passes import CheckCXDirection
from qiskit.transpiler import TranspilerError

from purestate import ConstantsStateOptimization, PureStateOnU


def level_3_with_contant_pure(pass_manager_config: PassManagerConfig) -> PassManager:
    """
    Args:
        pass_manager_config: configuration of the pass manager.

    Returns:
        a level 3 pass manager.
    """
    basis_gates = pass_manager_config.basis_gates
    coupling_map = pass_manager_config.coupling_map
    initial_layout = pass_manager_config.initial_layout
    layout_method = pass_manager_config.layout_method or 'dense'
    routing_method = pass_manager_config.routing_method or 'stochastic'
    seed_transpiler = pass_manager_config.seed_transpiler
    backend_properties = pass_manager_config.backend_properties

    # 1. Unroll to the basis first, to prepare for noise-adaptive layout
    _unroll = Unroller(basis_gates + ['annotation'])

    # 2. Layout on good qubits if calibration info available, otherwise on dense links
    _given_layout = SetLayout(initial_layout)

    def _choose_layout_condition(property_set):
        return not property_set['layout']

    _choose_layout_1 = CSPLayout(coupling_map, call_limit=10000, time_limit=60)
    if layout_method == 'trivial':
        _choose_layout_2 = TrivialLayout(coupling_map)
    elif layout_method == 'dense':
        _choose_layout_2 = DenseLayout(coupling_map, backend_properties)
    elif layout_method == 'noise_adaptive':
        _choose_layout_2 = NoiseAdaptiveLayout(backend_properties)
    else:
        raise TranspilerError("Invalid layout method %s." % layout_method)

    # 3. Extend dag/layout with ancillas using the full coupling map
    _embed = [FullAncillaAllocation(coupling_map), EnlargeWithAncilla(), ApplyLayout()]

    # 4. Unroll to 1q or 2q gates, swap to fit the coupling map
    _swap_check = CheckMap(coupling_map)

    def _swap_condition(property_set):
        return not property_set['is_swap_mapped']

    _swap = [BarrierBeforeFinalMeasurements(), Unroll3qOrMore()]
    if routing_method == 'basic':
        _swap += [BasicSwap(coupling_map)]
    elif routing_method == 'stochastic':
        _swap += [StochasticSwap(coupling_map, trials=200, seed=seed_transpiler)]
    elif routing_method == 'lookahead':
        _swap += [LookaheadSwap(coupling_map, search_depth=5, search_width=6)]
    else:
        raise TranspilerError("Invalid routing method %s." % routing_method)

    # 5. 1q rotation merge and commutative cancellation iteratively until no more change in depth
    _depth_check = [Depth(), FixedPoint('depth')]

    def _opt_control(property_set):
        return not property_set['depth_fixed_point']

    _opt = [RemoveResetInZeroState(),
            Collect2qBlocks(), ConsolidateBlocks(),
            Unroller(basis_gates),  # unroll unitaries
            Optimize1qGates(basis_gates), CommutativeCancellation(),
            OptimizeSwapBeforeMeasure(), RemoveDiagonalGatesBeforeMeasure()]

    # 6. Fix any CX direction mismatch
    _direction_check = [CheckCXDirection(coupling_map)]

    def _direction_condition(property_set):
        return not property_set['is_direction_mapped']

    _direction = [CXDirection(coupling_map)]

    # Build pass manager
    pm = PassManager()
    pm.append(ConstantsStateOptimization())
    pm.append(_unroll)
    if coupling_map:
        pm.append(_given_layout)
        pm.append(_choose_layout_1, condition=_choose_layout_condition)
        pm.append(_choose_layout_2, condition=_choose_layout_condition)
        pm.append(_embed)
        pm.append(_swap_check)
        pm.append(_swap, condition=_swap_condition)
    pm.append(ConstantsStateOptimization())
    pm.append([Unroller(basis_gates+['swap', 'aswap', 'annotation']),
               Optimize1qGates(), PureStateOnU()])
    pm.append(_depth_check + _opt, do_while=_opt_control)
    if coupling_map and not coupling_map.is_symmetric:
        pm.append(_direction_check)
        pm.append(_direction, condition=_direction_condition)
    return pm
