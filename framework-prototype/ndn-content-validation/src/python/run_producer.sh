unset PYTHONPATH
echo "Running producer: $3"
"$2"/n$3.conf/ndn-content-validation/src/python/producer.py "$1" $3
