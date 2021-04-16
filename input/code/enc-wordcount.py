#
# Access to this file is granted under the SCONE SOURCE CODE LICENSE V1.0 
#
# Commercial use of any product using this file requires a commercial 
# license from scontain UG, www.scontain.com.
#
# also see https://sconedocs.github.io
#
# Copyright (C) 2019 Scontain UG
#

from __future__ import print_function

import sys, time
import os, pyaes, binascii
from operator import add

from pyspark.sql import SparkSession
import time

key = "Scontain-Germany"
aes = pyaes.AESModeOfOperationCTR(key)

def decrypt_m(e_mess):
    b_mess = binascii.unhexlify(e_mess)
    decrypted = aes.decrypt(b_mess)
    return decrypted

# Modify wordcount example of native PySpark
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: wordcount <file>", file=sys.stderr)
        sys.exit(-1)

    spark = SparkSession\
        .builder\
        .master(sys.argv[2])\
        .appName("PythonWordCount")\
        .getOrCreate()
    lines = spark.read.format("text").load(sys.argv[1]).rdd.map(lambda r: r[0])
    counts = lines.map(lambda x: decrypt_m(x)).flatMap(lambda x: x.split(' ')) \
                  .map(lambda x: (x, 1)) \
                  .reduceByKey(add)
    output = counts.collect()

    # Generate delay to allow window for memory attack
    print("###########################################")
    print("################ SLEEP 10 #################")
    print("###########################################")

    time.sleep(10)
    for (word, count) in output:
        print("%s: %i" % (word, count))

spark.stop()
