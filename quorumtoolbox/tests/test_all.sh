#!/usr/bin/env bash

set -E

cd $(cd -P -- "$(dirname -- "$0")" && pwd -P)

all_tests=(
	"test_constellation.py"
	"test_tessera.py"
	"test_raft.py"
	"test_ibft.py"
	"test_geth.py"
	"test_quorum_node.py raft"
	"test_quorum_node.py ibft"
	"test_quorum_network.py raft"
	"test_quorum_network.py ibft"
)


function handle_error {
    local retval=$?
    echo ":( Failed"
    exit $retval
}

trap handle_error ERR

cleardirs () {
    rm -r company1_q2_n* 2>>/dev/null
}

makedir () {
    cp -r ../template_dir company1_q2_n"$1"
}

run_tests () {
   tests=("$@")
   for test in "${tests[@]}";
      do
		echo "Running ${test}"
		makedir 0
		makedir 1
		python3 ${test}
		cleardirs
      done
}

makedir 999
cleardirs

run_tests "${all_tests[@]}"

echo "+ Passed"
