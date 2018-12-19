# Quorum Toolbox

## Dependencies
* python 3.5^
* [constellation v0.3.2](https://github.com/jpmorganchase/constellation) (this will install the binary `constellation-node`)
* [quorum v2.1.1](https://github.com/jpmorganchase/quorum/tree/v2.1.1) (`geth`, `bootnode`)

## Works on

* Ubuntu 16.04.4 LTS
* macOS 10.14

## Installation

Clone repo, cd to quorum-toolbox and run `python setup.py develop`.

**Constellation:** https://github.com/jpmorganchase/constellation#installation-from-source

## Testing

### Full test
This test creates necessary artifacts for a two node Quorum network. This includes creation of Constellation, Raft, Geth as well as other components and artifacts required for the network. This test uses the subtests which are listed below.

*If this test successfully completes, the subtests need not be run.*

* In main repo directory, execute ```tests/test_all.sh```. Each components of the Quorum Network will then be created locally
and tested.

### Subtests

**Constellation:**
This test creates necessary artifacts for a new Constellation component. Launches Constellation as a local process using the created artifacts, checks for the launched process and artifact consistency. Shutsdown the launched process on end.

1. In repo main directory, make a new copy of the folder template_dir ```cp -r template_dir company1_q2_n0```. If company1_q2_n0 is already present, delete it first.
2. Run ```python3 test_constellation.py```
3. Once test has completed successfully, do a diff of template_dir and company1_q2_n0 to find all the created artifacts.

**Raft:**
This test creates neccessary artifacts for a new Raft component. Checks for artifact consistency. Since Raft can't be launched on it own, this test does not attempt to launch Raft as a process.

1. In repo main directory, make a new copy of the template_dir ```cp -r template_dir company1_q2_n0```. If company1_q2_n0 is already present, delete it first.
2. Run ```python3 test_raft.py```
3. Once test has completed successfully, do a diff of template_dir and company1_q2_n0 to find all the created artifacts.

**Geth:**
This test creates neccessary artifacts for a new Geth component. Checks for artifact consistency. (TODO Launch Geth and do further checks on process and artifacts)

1. In repo main directory, make a new copy of the template_dir ```cp -r template_dir company1_q2_n0```. If company1_q2_n0 is already present, delete it first.
2. Run ```python3 test_geth.py```
3. Once test has completed successfully, do a diff of template_dir and company1_q2_n0 to find all the created artifacts.
