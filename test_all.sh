#!/usr/bin/env bash

# Run in pipenv virtual env

set -u
set -e

cleardirs () {
    rm -r company1_q2_n* 2>>/dev/null
}

makedir () {
    echo "Making directory company1_q2_n$1"
    cp -r template_dir company1_q2_n$1
}

checkresult() {
    if [ $1 -ne 0 ]
    then
        echo "FAILED"
        exit
    else
        echo "" #success!
    fi

}


echo "========================== STARTING ==========================="
makedir 999
cleardirs

makedir 0
python3 test_constellation.py
checkresult $?
cleardirs

makedir 0
python3 test_raft.py
checkresult $?
cleardirs

makedir 0
python3 test_geth.py
checkresult $?
cleardirs

makedir 0
python3 test_quorum_node.py
checkresult $?
cleardirs

makedir 0
makedir 1

python3 test_quorum_network.py
checkresult $?
cleardirs

echo "========================= FINISHED =============================="
