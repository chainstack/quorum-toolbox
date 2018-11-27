# quorum-toolbox &middot; [![Build Status](https://img.shields.io/travis/npm/npm/latest.svg?style=flat-square)](https://travis-ci.org/npm/npm) [![npm](https://img.shields.io/npm/v/npm.svg?style=flat-square)](https://www.npmjs.com/package/npm) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com) [![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](https://github.com/your/your-project/blob/master/LICENSE)

## HOWTO

#### Dependencies
* python 3.5^
* [constellation v0.3.2](https://github.com/jpmorganchase/constellation) (this will install the binary `constellation-node`)
* [quorum v2.1.1](https://github.com/jpmorganchase/quorum/tree/v2.1.1) (`geth`, `bootnode`)

#### Works on

* Ubuntu 16.04.4 LTS
* macOS 10.14



**Clone Repo and cd to quorum-toolbox and run `python setup.py develop`**

**Full test:**
This test creates necessary artifacts for a two node
Quorum network. This includes creation of Constellation,
Raft, Geth as well as other components and artifacts required
for the network. This test uses the subtests which are listed below.

*If this test successfully completes, the subtests need not be run.*

* In main repo directory, execute ```tests/test_all.sh```. Each components of the Quorum Network will then be created locally
and tested.

___

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
___
