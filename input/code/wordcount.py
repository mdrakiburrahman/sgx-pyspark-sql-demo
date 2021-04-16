from __future__ import print_function

import sys, time
from operator import add

from pyspark import SparkContext

import os

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: wordcount <file>", file=sys.stderr)
        exit(-1)
    sc = SparkContext(sys.argv[2], appName="PythonWordCount")

    lines = sc.textFile(sys.argv[1], 1)
    counts = lines.flatMap(lambda x: x.split(' ')) \
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

sc.stop()
