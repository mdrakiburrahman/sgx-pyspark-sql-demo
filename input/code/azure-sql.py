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

    # Loading encrypted columns - no CMK required
    EncryptedDF = spark.read \
        .format("jdbc") \
        .option("url", "") \
        .option("dbtable", "dbo.Employees") \
        .load()

    EncryptedDF.limit(10) \
               .show()

    # Loading unencrypted columns - with CMK
    UnencryptedDF = spark.read \
        .format("jdbc") \
        .option("url", "") \
        .option("dbtable", "dbo.Employees") \
        .load()

    UnencryptedDF.limit(10) \
                 .show()

    # Generate delay to allow window for memory attack
    print("###########################################")
    print("################ SLEEP 10 #################")
    print("###########################################")
    time.sleep(10)

    spark.stop()
