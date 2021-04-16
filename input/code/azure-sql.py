from __future__ import print_function

import sys, time
from operator import add
import os

from pyspark.sql import SparkSession

if __name__ == "__main__":
    spark = SparkSession \
        .builder \
        .appName("Azure SQL application") \
        .getOrCreate()

    df = spark.read.option("header",True) \
                   .option("inferSchema",True) \
                   .csv("input/data/dbo-Employees.csv")

    df.show()

    spark.stop()