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
        .option("url", "jdbc:sqlserver://aiaconfidentialserver.database.windows.net:1433;database=ContosoHR;user=boor@aiaconfidentialserver;password=acntorPRESTO!;columnEncryptionSetting=enabled;enclaveAttestationUrl=https://aiaconfidentialatst.eus.attest.azure.net/attest/SgxEnclave;enclaveAttestationProtocol=AAS;keyVaultProviderClientId=72b8dc93-6305-4fe2-aed7-d73f5837b008;keyVaultProviderClientKey=~fZ~043-ien18yI.tPlTNwCrmgwsg58~Un;") \
        .option("dbtable", "dbo.Employees") \
        .load()

    jdbcDF.show()

    spark.stop()