#Run logio
./start-log-service.sh

#Native PySpark
/spark/bin/spark-submit input/wordcount.py  input/sensitive-input.txt  spark://$(hostname -f):7077 &> output.txt &

#PySpark with ecrypted input
/spark/bin/spark-submit input/enc-wordcount.py  input/encrypted-sensitive-input.txt  spark://$(hostname -f):7077 &> output.txt &

#Memory attack
./memory-dump.sh

#SGX-PySpark with SCONE
/spark/bin/spark-submit encrypted-files/enc-wordcount.py  input/encrypted-sensitive-input.txt  spark://$(hostname -f):7077 &> output.txt &
