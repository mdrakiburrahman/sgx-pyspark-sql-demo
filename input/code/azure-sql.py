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

    # Loading data from a CSV source
    df = spark.read.option("header",True) \
                   .option("inferSchema",True) \
                   .csv("input/data/dbo-Employees.csv")

    df.show()

    # Loading data from a JDBC source
    jdbcDF = spark.read \
        .format("jdbc") \
        .option("url", "") \
        .option("dbtable", "dbo.Employees") \
        .load()

    jdbcDF.show()

    spark.stop()
