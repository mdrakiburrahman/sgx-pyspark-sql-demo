from __future__ import print_function

import sys, time
from operator import add
import os

from pyspark.sql import SparkSession

if __name__ == "__main__":
    # Generate delay to allow window for memory attack
    print("###########################################")
    print("######### Starting Spark Session ##########")
    print("###########################################")

    # Start SparkSession
    spark = SparkSession \
        .builder \
        .appName("NYC TAXI YELLOW") \
        .getOrCreate()

    # Azure storage access info
    blob_account_name = "azureopendatastorage"
    blob_container_name = "nyctlc"
    blob_relative_path = "yellow"
    blob_sas_token = r""
    
    # Allow SPARK to read from Blob remotely
    wasbs_path = 'wasbs://%s@%s.blob.core.windows.net/%s' % (blob_container_name, blob_account_name, blob_relative_path)
    spark.conf.set(
      'fs.azure.sas.%s.%s.blob.core.windows.net' % (blob_container_name, blob_account_name),
      blob_sas_token)
    print('Remote blob path: ' + wasbs_path)
    
    # SPARK read parquet, note that it won't load any data yet by now
    start_time = time.time()
    df = spark.read.parquet(wasbs_path)
    print(df.count())
    print("Took roughly: ", time.time()-start_time)

    spark.stop()

    # Generate delay to allow window for memory attack
    print("###########################################")
    print("#### Generate window for Memory Attack ####")
    print("###########################################")
    print("################ SLEEP 10 #################")
    print("###########################################")
    time.sleep(10)
