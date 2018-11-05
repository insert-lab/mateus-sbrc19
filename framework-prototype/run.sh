#!/bin/bash
# This script:
#             used for configure the blockchain scenario over the Core simulator
#
# Actions:
#         - Copy the ndn-content-validation dir to /tmp/pycore.XXXX/blockchain
#         - Unset the PYTHONPATH on nodes (BUG)
#         - Start the ganache-cli -h 10.0.0.23 on blockchain node
#         - Migrate the contract
#         - Start the producer by sending an interest with the content informations about the provided content
#         - Consumer ask for the content but the answer comes from an unauthorized_producer
#         - unauthorized_producer ask for permission to producer
#         -
#         - Total of 10 nodes, which 3 are consumers, 4 are producers, and 3 are malicious producers
#         - Pode haver dois tipos de ataques:
#         - O malicious node encaminha o interest e espera pelo pacote de dados para entao altera-lo
#           ou ao receber o pacote forja um payload e insere sua chave no lugar da do produtor



if [ $# -lt 1 ] ; then
    echo "Usage: $0 num_nodes"
    exit
fi

# A dict
declare -A used_accounts

# Number of nodes
n_nodes=$1

# Set random seed
RANDOM=2129
# RANDOM=3203

# emulation parameters
n_producers=2
n_consumers=3
n_attackers=0

# Global VARS
core_dir=$(echo /tmp/pycore.*)
[ -z "$core_dir" ] && exit -1
contract_address=""

# ////////////////////////////////  Install functions

blockchain(){
  echo "Starting BC"
  cp -a ndn-content-validation "$core_dir/blockchain.conf"

  /usr/local/bin/vcmd -c "$core_dir/blockchain" -- /home/mateus/.npm_global/bin/ganache-cli -h 10.0.1.20 -p 7545 -a $((n_nodes+1)) &
  /usr/local/bin/vcmd -c "$core_dir/blockchain" -- bash -c "cd $core_dir/blockchain.conf/ndn-content-validation && /home/mateus/.npm_global/bin/truffle migrate > /tmp/output"
}

install_producer(){
  contract_address=$(grep -i "ContentValidation:" /tmp/output | awk -F':' '{print $2}' | tr -d ' ')
  cp -a ndn-content-validation "$core_dir/n${node_id}.conf"
  node_id=$1
  cp -a ndn-content-validation "$core_dir/n${node_id}.conf"
  /usr/local/bin/vcmd -c "$core_dir/n${node_id}" -- bash "$core_dir"/n${node_id}.conf/ndn-content-validation/src/python/run_producer.sh "$contract_address" "$core_dir" "$node_id" &
}

install_consumer(){
  node_id=$1
  cp -a ndn-content-validation "$core_dir/n${node_id}.conf"
  /usr/local/bin/vcmd -c "$core_dir/n${node_id}" -- bash "$core_dir"/n${node_id}.conf/ndn-content-validation/src/python/run_consumer.sh "$contract_address" "$core_dir" "$node_id" &
}

install_unauthorized_producer(){
  node_id=$1
  cp -a ndn-content-validation "$core_dir/n${node_id}.conf"
  /usr/local/bin/vcmd -c "$core_dir/n${node_id}" -- bash "$core_dir"/n${node_id}.conf/ndn-content-validation/src/python/release_evil.sh "$contract_address" "$core_dir" "$1" &
}

install_router(){
  cp -a ndn-content-validation "$core_dir/n${1}.conf"
  /usr/local/bin/vcmd -c "$core_dir/n${1}" -- bash "$core_dir"/n${1}.conf/ndn-content-validation/src/python/router.sh "$core_dir" "$1" &
}

# ///////////////////// Run experiments

# Start blockchain
blockchain

# Copy ABI to a Global directory
cp "$core_dir"/blockchain.conf/ndn-content-validation/build/contracts/ContentValidation.json /tmp/

for (( i = 0; i < $n_producers; i++ )); do
  id=$(($RANDOM % $n_nodes+1))
  if [ ! ${used_accounts[$id]} ]
  then
    used_accounts[$id]=true
    echo "Installing producer app on node $id"
    # Install producers
    install_producer $id
  else
      let i--
  fi
done

for (( i = 0; i < $n_consumers; i++ )); do
  id=$(($RANDOM % $n_nodes+1))
  if [ ! ${used_accounts[$id]} ]
  then
    used_accounts[$id]=true
    echo "Installing consumer app on node $id"
    # Install consumers
    install_consumer $id
  else
      let i--
  fi
done

for (( i = 0; i < $n_attackers; i++ )); do
  id=$(($RANDOM % $n_nodes+1))
  if [ ! ${used_accounts[$id]} ]
  then
    used_accounts[$id]=true
    echo "Installing unauthorized_producer app on node $id"
    # Install malicious producers
    install_unauthorized_producer $id
  else
      let i--
  fi
done

# Install router Function on remaining nodes
for (( i = 1; i <= $n_nodes; i++ )); do
  if [ ! ${used_accounts[$i]} ]
  then
    # Install routers
    echo "Installing router app on node $i"
    used_accounts[$i]=true
    install_router $i
  fi
done
