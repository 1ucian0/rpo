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

from qiskit.transpiler import PassManagerConfig
from qiskit.transpiler.coupling import CouplingMap


class Result:
    def __init__(self, circuit, backend):
        self.input_circuit = circuit
        self.n_qubits = len(circuit.qubits)
        self.depth = circuit.depth()
        self.pms_results = {}
        self.backend = backend

    @staticmethod
    def pm_config(seed, backend):
        return PassManagerConfig(
            initial_layout=None,
            basis_gates=['u1', 'u2', 'u3', 'cx', 'id'],
            coupling_map=CouplingMap(backend().configuration().coupling_map),
            backend_properties=backend().properties(),
            seed_transpiler=seed)

    def run_pm_with_time(self, passmanager, seed):
        times = {'total': 0}
        repetition = {}

        def collect_time(**kwargs):
            times['total'] += kwargs['time']
            passname = type(kwargs['pass_']).__name__
            if passname in times:
                times[passname] += kwargs['time']
                repetition[passname] += 1
            else:
                times[passname] = kwargs['time']
                repetition[passname] = 0

        pm = passmanager(Result.pm_config(seed, self.backend))
        transpiled = pm.run(self.input_circuit, callback=collect_time)

        return transpiled, times, repetition

    def run_pms(self, passmanagers, times=10):
        for pm in passmanagers:
            result = {'transpiled': [], 'times': {}, 'repetitions': {}}
            for seed in range(times):
                transpiled, calls, repetitions = self.run_pm_with_time(pm, seed)
                result['transpiled'].append(transpiled)
                for passname, time in calls.items():
                    if passname in result['times']:
                        result['times'][passname].append(time)
                    else:
                        result['times'][passname] = [time]
                for passname, rep in repetitions.items():
                    if passname in result['repetitions']:
                        result['repetitions'][passname].append(rep)
                    else:
                        result['repetitions'][passname] = [rep]

            self.pms_results[pm.__name__] = result

    def row(self, fields):
        return {field: getattr(self, field) for field in fields}

    @property
    def level3_loop_iterations(self):
        return self.pms_results['level_3_pass_manager']['repetitions']['ConsolidateBlocks']

    @property
    def we_loop_iterations(self):
        return self.pms_results['level_3_with_contant_pure']['repetitions']['ConsolidateBlocks']

    @property
    def level3_cxs(self):
        cx_results = []
        for cx_result in self.pms_results['level_3_pass_manager']['transpiled']:
            cx_results.append(cx_result.count_ops()['cx'])
        return cx_results

    @property
    def level2_cxs(self):
        cx_results = []
        for cx_result in self.pms_results['level_2_pass_manager']['transpiled']:
            cx_results.append(cx_result.count_ops()['cx'])
        return cx_results

    @property
    def we_cxs(self):
        cx_results = []
        for cx_result in self.pms_results['level_3_with_contant_pure']['transpiled']:
            cx_results.append(cx_result.count_ops()['cx'])
        return cx_results[0] if len(cx_results) == 1 else cx_results
    
    @property
    def level3_depth(self):
        depth_results = []
        for sample in self.pms_results['level_3_pass_manager']['transpiled']:
            depth_results.append(sample.depth())
        return depth_results[0] if len(depth_results) == 1 else depth_results

    @property
    def level2_depth(self):
        depth_results = []
        for sample in self.pms_results['level_2_pass_manager']['transpiled']:
            depth_results.append(sample.depth())
        return depth_results[0] if len(depth_results) == 1 else depth_results

    @property
    def we_depth(self):
        depth_results = []
        for sample in self.pms_results['level_3_with_contant_pure']['transpiled']:
            depth_results.append(sample.depth())
        return depth_results[0] if len(depth_results) == 1 else depth_results

    @property
    def level3_gate_count(self):
        size_results = []
        for sample in self.pms_results['level_3_pass_manager']['transpiled']:
            size_results.append(sample.size())
        return size_results[0] if len(size_results) == 1 else size_results

    @property
    def level2_gate_count(self):
        size_results = []
        for sample in self.pms_results['level_2_pass_manager']['transpiled']:
            size_results.append(sample.size())
        return size_results

    @property
    def we_gate_count(self):
        size_results = []
        for sample in self.pms_results['level_3_with_contant_pure']['transpiled']:
            size_results.append(sample.size())
        return size_results[0] if len(size_results) == 1 else size_results

    @property
    def level2_time(self):
        return self.pms_results['level_2_pass_manager']['times'].get('total', None)

    @property
    def level3_time(self):
        return self.pms_results['level_3_pass_manager']['times'].get('total', None)

    @property
    def we_time(self):
        return self.pms_results['level_3_with_contant_pure']['times'].get('total', None)

    @property
    def l3_swapper_time(self):
        return self.pms_results['level_3_pass_manager']['times'].get('StochasticSwap', None)

    @property
    def l2_swapper_time(self):
        return self.pms_results['level_2_pass_manager']['times'].get('StochasticSwap', None)

    @property
    def we_swapper_time(self):
        return self.pms_results['level_3_with_contant_pure']['times'].get('StochasticSwap', None)

    @property
    def our_passes_time(self):
        times = self.pms_results['level_3_with_contant_pure']['times']
        return [sum(i) for i in zip(times.get('ConstantsStateOptimization', 0),
                                    times.get('PureStateOnU', 0))]
