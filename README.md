# Quorum Toolbox

[![CircleCI](https://circleci.com/gh/chainstack/quorum-toolbox/tree/master.svg?style=svg&circle-token=c64e8d715eee5747f4ab9f9e0321dc558f3ec92f)](https://circleci.com/gh/chainstack/quorum-toolbox/tree/master)
[![PyPI version](https://badge.fury.io/py/quorumtoolbox.svg)](https://badge.fury.io/py/quorumtoolbox)

## Dependencies

* Python ^3.4
* [constellation v0.3.2](https://github.com/jpmorganchase/constellation) (`constellation-node`)
* [quorum v2.4.0](https://github.com/jpmorganchase/quorum) (`geth`, `bootnode`)
* [istanbul-tools 1.0.1](https://github.com/jpmorganchase/istanbul-tools) (`istanbul`)

## Installation

    pip install quorumtoolbox

## Development

Clone repo, cd to quorum-toolbox and run `python setup.py develop`.

## Testing

    docker-compose up
