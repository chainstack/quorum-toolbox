#!/bin/bash

set -e							# exit if any cmd fails with exit code != 0
set -o pipefail						# exit if any cmd in a pipline fails with exit code != 0

# -------------------------------- Read and set args --------------------------------------------
CONFIG_FILE="quorum_node_config.sh"

echo "[*] Getting config from $CONFIG_FILE"
source $CONFIG_FILE

GETH_ARGS="$DATADIR $NODISCOVER $NETWORKID $PORT $VERBOSITY $UNLOCK $PASSWORD"
RPC_ARGS="$RPC $RPCADDR $RPCPORT $RPCAPI $RPCCORSDOMIAN"
RAFT_ARGS="$RAFT $RAFTPORT $RAFTJOINEXISTING $MAXPEERS $RAFTBLOCKTIME"
#WS_ARGS="$WS $WSADDR $WSPORT $WSAPI $WSORIGINS"
#OTHER_ARGS="$EMITCHECKPOINTS $TARGETGASLIMIT $SHH $NAT"

#---------------------------------- Process genesis block ----------------------------------------
echo "[*] Checking if genesis block needs to be mined..."

if [ ! -d $CHAINDATADIR ]; then
  echo "[*] $CHAINDATADIR not found. Mining..."
  $GETH_BINARY $DATADIR init genesis.json
  echo "[*] Done"
else
  echo "[*] $CHAINDATADIR found. Not mining."
fi

#--------------------------------- Start constellation ------------------------------------------
cd ../constellation

echo "[*] Starting Constellation node with args:"
echo "[*] $CONSTELLATION_BINARY $CONSTELLATION_CONFIG_FILE $CONSTELLATION_LOG_FILE"

#TODO: Cant the launch_constellation script be used instead?
nohup $CONSTELLATION_BINARY $CONSTELLATION_CONFIG_FILE 2>> $CONSTELLATION_LOG_FILE &

# Give some time to create constellation tls certs if needed
sleep 5

echo "Waiting for constellation ipc file to be created..."

# Wait till constellation starts and ipc file gets generated
while : ; do
    sleep 1

    re=$CONSTELLATION_IPC_FILE_NAME
	enodestr=$(ls -al)
 
    if [[ $enodestr =~ $re ]];then
        break;
    fi
done

echo "[*] Checking if constellation node is running"
netstat -lupnt |  grep -i "constellation"

echo "[*] Constellation running."

#-------------------------------- Start Quorum node -----------------------------------------
cd ../blockchain

echo "[*] Geth Verions:"
geth version | grep -i "version"

QUORUM_ARGS="$GETH_ARGS $RAFT_ARGS $RPC_ARGS"
echo "[*] Starting Quorum node with args:"
echo "$QUORUM_ARGS"

echo "[*] Launching Quorum node...(this will not return)"

PRIVATE_CONFIG=../constellation/"$CONSTELLATION_IPC_FILE" nohup  "$GETH_BINARY" "$QUORUM_ARGS" 2>>"$GETH_LOG_FILE" &

#------------------------------------------------------------------------------------------
# Give some time for geth to start
sleep 5

echo "[*] Checking if constellation node is running"
netstat -lupnt |  grep -i "geth"
echo "[*] Done"

echo "[*] All Done"
