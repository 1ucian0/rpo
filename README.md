# Relaxed Peephole Optimization
This repository contains artifacts and test files to reproduce experiments from the CGO 2021 paper "Relaxed Peephole Optimization: A Novel Compiler Optimization for Quantum Circuits" by Ji Liu, Luciano Bello, and Huiyang Zhou


Use at your own risk! In no event shall the authors be liable for any damages whatsoever (including without limitation damages for loss of business profits, business interruption, loss of business information, or any other pecuniary loss) arising from the use of or inability to use the software, even if the authors have been advised of the possibility of such damages.

If you have any questions feel free to contact us using jliu45@ncsu.edu

System pre-requisities for Qiskit
========================
* Ubuntu 16.04 or later
* macOS 10.12.6 or later
* Windows 7 or later

Software pre-requisites
=======================

* Python 3.5+
* Qiskit version 0.18
* Jupyter notebook
* matplotlib 3.3
* z3-solver
* tabulate

## Installation and test

```
pip install -r requirements.txt
python -m unittest discover -v tests
```

## Run benchmarks

```
python run_benchmark.py benchmark/random.yaml
```

The result will be dump in `results/random.csv` in this case. In general, in 
`python run_benchmark.py benchmark/<something>.yaml` dumps in`results/<something>.csv`.

## Run experiments on real device

Run the corresponding jupyter notebooks: QPE_almaden/melbourne/rochester.

## Benchmark options

The way to set options for a benchmark is via a yaml file with the following format:

```yaml
# Location of the suite in which circuits() leaves.
# circuits() yield circuits to test. 
suite: benchmark.suites.random

# Optional. How many times a transpiled procees should run. 
times: 3

# Optional. Backend for PassManagerConfig. Default is FakeMelbourne
backend: qiskit.test.mock:FakeMelbourne

# A list of pass managers to run. 
pass managers:
  - qiskit.transpiler.preset_passmanagers:level_3_pass_manager
  - passmanager:level_3_with_contant_pure

# A list of fields to collect. They should be attributes of
# benchmark.utils.Result class.
fields:
  - n_qubits
  - depth
  - level3_cxs
  - we_cxs
```
