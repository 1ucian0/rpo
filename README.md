# purestate


- `|0>` and `|1>` are *constants*
- Single qubit gates conserve *pure state*
- *constants* are particular case of *pure states*
 

## Installation and test

```
pip install -r requirements.txt
python -m unittest discover -v tests
```

## Run benchmarks

```
./run_benchmark.py benchmark/random.yaml
```

The result will be dump in `results/random.csv` in this case. In general, in 
`./run_benchmark.py benchmark/<something>.yaml` dumps in`results/<something>.csv`.

## Run experiments on real device

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
