# SGX-PySpark Demo

This repository contains SGX-PySpark demo.

## Video

[SGX-PySpark demo](https://youtu.be/yI3iEFWUWbU)

## Details
First, please shoot us (info@scontain.com) an email providing your Docker ID to get access to the Docker image: `registry.scontain.com:5050/sconecuratedimages/www2019:sgx-pyspark`

Try it out by executing:

```bash
git clone https://github.com/scontain/sgx-pyspark-demo && cd sgx-pyspark-demo 
```

```bash
docker run -it --rm -v `pwd`:/fspf  --privileged -p 8080:8080 -p 6868:6868 -p 28778:28778 registry.scontain.com:5050/sconecuratedimages/www2019:sgx-pyspark sh
```

Start Apache Spark and test it with *pi* application:

```bash
/test.sh
```

Go to the demo directory:

```bash
 cd /fspf/
```

Create a file system protection file (meta file) to store all the metadata required for checking the consistency of files. 
Then add encrypted regions and encrypt the input PySpark codes and data. Store the encryption key and the tag of the fspf to the file keytag:

```bash
 ./fspf.sh
```

Export environment variables

```bash
export SCONE_FSPF_KEY=$(cat input/keytag | awk '{print $11}')
export SCONE_FSPF_TAG=$(cat input/keytag | awk '{print $9}')
export SCONE_FSPF=/fspf/encrypted-files/volume.fspf
```

Now, run the wordcount application with SGX-PySpark.

```bash
/spark/bin/spark-submit encrypted-files/enc-wordcount.py  input/encrypted-sensitive-input.txt  spark://$(hostname -f):7077 &> output.txt &
```

Try to dump memory of the application to steal secrets

```bash
./memory-dump.sh
```

## Contacts

Send email to do.le_quoc@tu-dresden.de
