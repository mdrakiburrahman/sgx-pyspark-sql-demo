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

    df = spark.read.csv("input/data/dbo-Employees.csv")

    df.show()

    spark.stop()