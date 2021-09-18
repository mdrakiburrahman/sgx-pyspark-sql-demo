# Confidential Analytics with Apache Spark on SGX-enabled Containers

## Overview

This repository demonstrates the following architecture for **Confidential Analytics** on Azure SGX enabled machines (**AKS** or **Standalone**) for running containerized applications: <br>

> 💡 Confidential analytics in this context is meant to imply: **_"run analytics on PII data with peace of mind against data exfiltration"_** - this includes potential `root`-level access breach both internally (rogue admin) or externally (system compromise).

![Architecture Diagram](images/Architecture-Diagram.png)

### Goal

Demonstrate how to run **end-to-end Confidential Analytics** on Azure (presumably on PII data), leveraging [Azure SQL Always Encrypted with Secure Enclaves](https://docs.microsoft.com/en-us/sql/relational-databases/security/encryption/always-encrypted-enclaves?view=sql-server-ver15) as the database, and containerized **Apache Spark** on SGX-enabled Azure machines for analytics workloads.

## Live Demo

[![SCONE: Secure Linux Containers with Intel SGX](https://img.youtube.com/vi/em6ovuznAf8/0.jpg)](https://youtu.be/em6ovuznAf8)

### Key points

- **Azure DC Series**: We run a containerized [Spark 3.1.1](https://spark.apache.org/releases/spark-release-3-1-1.html) application, on an [**Azure DC4s_v2**](https://docs.microsoft.com/en-us/azure/virtual-machines/dcv2-series) machine running Docker. These machines are backed by the latest generation of Intel XEON E-2288G Processor with [SGX extensions](https://software.intel.com/content/www/us/en/develop/topics/software-guard-extensions.html) - the **_key component_** to enabling the core message of this demo.
  - **💡 Note**: This demo works identically well on [AKS running DC4s_v2 nodes](https://docs.microsoft.com/en-us/azure/confidential-computing/confidential-computing-enclaves). We perform the demo on the standalone node to enjoy the additional benefits of RDP for demonstrations purposes that `kubectl` wouldn't allow as easily.
- **SCONE**: To run Spark inside an SGX enclave - we leverage [SCONE](https://docs.microsoft.com/en-us/azure/confidential-computing/confidential-containers#scone-scontain), who have essentially taken the [Open Source Spark code](https://sconedocs.github.io/sconeapps_spark/), and wrapped it with their runtime so that Spark can run inside SGX enclaves (a task that requires deep knowledge of the SGX ecosystem - something SCONE is an expert at).

  - **Introduction**: Here's a fantastic video on SCONE from one of the founders - [Professor Christof Fetzer](https://github.com/christoffetzer): <br>
    [![Scone walkthrough](https://img.youtube.com/vi/aoA8pwasMqs/0.jpg)](https://youtu.be/aoA8pwasMqs)
  - **Deep dive**: If you're looking for deeper material on SCONE, here's an academic paper describing the underlying mechanics: [link](https://www.usenix.org/system/files/conference/osdi16/osdi16-arnautov.pdf)
  - **Deep dive w/ commentary**: This is an entertaining walkthrough of the above paper by [Jessie Frazelle](https://github.com/jessfraz) - also a leader in the Confidential Computing space. <br>
    [![SCONE: Secure Linux Containers with Intel SGX](https://img.youtube.com/vi/3UYczEYrxuY/0.jpg)](https://youtu.be/3UYczEYrxuY)

  - **Sconedocs**: Scone's official documentation for getting started: [link](https://sconedocs.github.io/)

### Pre-requisites

1. Registry for access to the 2 Spark images used per scenario:
   - `#TODO`
2. Follow the tutorial here to deploy an Azure SQL Always Encrypted with Secure Enclaves Database with some sample PII data: [link](https://docs.microsoft.com/en-us/azure/azure-sql/database/always-encrypted-enclaves-getting-started)
3. A **DC4s_v2** VM deployment (standalone or in AKS cluster)
   - **Scenario 1** (baseline) can run on any machine (including the DC4s_v2 machine). I perform it on my Surface laptop 3.
   - **Scenario 2** will not work without SGX - i.e. must run on an Azure DC series machine. You can enable [xfce](https://www.xfce.org/) to get an RDP interface.

## Scenario 1: Spark job running on non-SGX hardware

![Scenario 1](images/Scenario-1.png)

**Setup**

1. RDP into VM/laptop
2. Navigate to `http://localhost:28778/` [(log.io)](https://github.com/NarrativeScience/log.io) and `localhost:8080/` [(Spark Web UI)](https://spark.apache.org/docs/3.0.0-preview/web-ui.html)

**Execute steps**

```bash
# Run Container
docker run -it --rm --name "sgx_pyspark_sql" --privileged -p 8080:8080 -p 6868:6868 -p 28778:28778 aiaacireg.azurecr.io/scone/sgx-pyspark-sql sh

# Explore Docker Entrypoint to see startup
vi /usr/local/bin/docker-entrypoint.sh

# Replace the JDBC endpoint before running job
vi input/code/azure-sql.py

# E.g. jdbc:sqlserver://your--server--name.database.windows.net:1433;database=ContosoHR;user=your--username@your--server--name;password=your--password;

# Scenario 1: Scone: Off | Data: Encrypted | Code: Plaintext
############################################################
# Run Spark job
/spark/bin/spark-submit --driver-class-path input/libraries/mssql-jdbc-9.2.1.jre8.jar input/code/azure-sql.py >> output.txt 2>&1 &

# Testing the memory attack
./memory-dump.sh

```

## Scenario 2: Spark with Scone running on SGX (DC4s_v2)

![Scenario 2](images/Scenario-2.png)

**Setup**

1. RDP into Azure DC VM (need xfce or similar desktop interface)
2. Navigate to `http://localhost:6688/#{%221618872518526%22:[%22spark|SCONE-PySpark%22]}` [(log.io - newer version)](https://github.com/NarrativeScience/log.io) and `localhost:8080/` [(Spark Web UI)](https://spark.apache.org/docs/3.0.0-preview/web-ui.html)

**Execute steps**

```bash
# Elevate to superuser for Docker
sudo su -

# Set SGX variable - for more information, see https://sconedocs.github.io/sgxinstall/
export MOUNT_SGXDEVICE="-v /dev/sgx/:/dev/sgx"

# Run Container
docker run $MOUNT_SGXDEVICE -it --rm --name "sgx_pyspark_3" --privileged -p 8080:8080 -p 6688:6688 aiaacireg.azurecr.io/scone/sgx-pyspark-3 sh

# Explore Docker Entrypoint to see startup
vi /usr/local/bin/docker-entrypoint.sh

# Replace the JDBC endpoint before running job
vi input/code/azure-sql.py

# E.g. jdbc:sqlserver://your--server--name.database.windows.net:1433;database=ContosoHR;user=your--username@your--server--name;password=your--password;columnEncryptionSetting=enabled;enclaveAttestationUrl=https://your--attestation--url.eus.attest.azure.net/attest/SgxEnclave;enclaveAttestationProtocol=AAS;keyVaultProviderClientId=your--sp--id;keyVaultProviderClientKey=your--sp--secret;

# Scenario 1: Scone: On | Data: CMK Protected | Code: Plaintext
###############################################################
# Run Spark job
/spark/bin/spark-submit --driver-class-path input/libraries/mssql-jdbc-9.2.0.jre8-shaded.jar input/code/azure-sql.py >> output.txt 2>&1 &

# Testing the memory attack
./memory-dump.sh

# Scenario 2: Scone: On | Data: CMK Protected | Code: Encrypted
###############################################################
# Show that there is no encrypted code
tree

# Encrypt code into fspf
source ./fspf.sh

# Show the encrypted code
tree
vi encrypted-files/azure-sql.py

# Run Spark job
/spark/bin/spark-submit --driver-class-path input/libraries/mssql-jdbc-9.2.0.jre8-shaded.jar encrypted-files/azure-sql.py >> output.txt 2>&1 &

# Testing the memory attack
./memory-dump.sh
```

## Scenario 3: Big Data processing with Spark with Scone running on Confidential AKS clusters

In this scenario, we leverage Spark with Scone on a Confidential AKS cluster to process larger datasets in a distributed fashion. The Dataset we use is the common [NYC Taxi](https://docs.microsoft.com/en-us/azure/open-datasets/dataset-taxi-yellow?tabs=pyspark) Dataset - where we demonstrate a simple Spark Job ([`COUNT *`](https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.sql.DataFrame.count.html)) on 1.5 Billion Rows of Parquet files (50 GB) stored on Azure Blob Storage:

![Scenario 3](images/Scenario-3.png)

The tasks are divided among the available executors (user configurable), which allows for horizontal scalability. The executors are written in Python and have their source code encrypted by the Scone filesystem protection features we've already discussed.

### A note about EPC Memory Size

The same protection guarantees as the previous scenarios apply here too. Kubernetes admins, or any privileged user, cannot inspect the in-memory contents or source code of driver or executors. If the dataset/task are too large to fit inside of the protected Intel SGX memory (EPC - which is up to **256 MB** for Intel E-2200 processors), the enclaves will use the main memory as a swap space. This process, however, does not violate security guarantees, as all the data that goes into main memory is encrypted with SGX-derived keys. The only theoretical drawback of swapping is the performance overhead of encrypting/decrypting the data (which as we'll see from a [benchmark](#benchmark) - is largely scenario dependent. since for this particular scenario we do not see any noticable performance drops).

> 💡 The size of the protected memory (EPC) supported by Intel [Ice Lake](https://www.intel.com/content/www/us/en/newsroom/news/xeon-scalable-platform-built-sensitive-workloads.html) chips is up to **512 GB**. Therefore, the upcoming arrival of Ice Lake hardware on Azure means EPC Memory size becomes equivalent to regular memory - i.e. irrelevant for practical performance purposes - while enforcing the elevated security guarantees we are observing here.

Either way, both with upcoming Ice Lake and with current-gen SGX chips, the ability to horizontally scale on "Big Data" (i.e. 50 GB+ - bigger than a single Pod can process - requiring distributing the computation across Pods) while enjoying realistic computation times means the techniques illustrated in this article is Production Ready regardless of the size of the data we're looking to process via Apache Spark on Scone.

### Running with Remote Attestation

Remote attestation ensures that your workload has not been tampered with when deployed to a untrusted host, such as a VM instance or a Kubernetes node that runs on the cloud. In this process, attestation evidence provided by Intel SGX hardware is analyzed by an attestation provider. To perform remote attestation on a Scone application (such as Spark driver and executor pods), two services are required:

- **Local Attestation Service (LAS)**: runs on the untrusted host and gathers the attestation evidence provided by Intel SGX about the application being attested. This evidence is signed and forwarded to CAS; and
- **Configuration and Attestation Service (CAS)**: a central service that manages security policies (called **Scone _sessions_**), configuration and secrets. CAS compares the attestation evidence gathered by LAS against the application's security policies (defined by the application owner) to decide whether the enclave is trustworthy of not. If so, CAS allows the enclave to run and securely injects configuration and secrets into it. [Learn more about CAS and its features, such as secret generation and access control](https://sconedocs.github.io/CASOverview/).

> 💡 The decision of whether the attestation evidence is trustworthy or not can be delegated to a third-party attestation provider, such as Intel Attestation Service or Microsoft Azure Attestation.

For this scenario, we use a [Public CAS](https://sconedocs.github.io/public-CAS/) provided by Scone for test purposes. In production scenarios you will control your own CAS - which also runs inside of enclaves and can be remotely attested.

#### Pre-requisite Setup

1. Configure `kubectl` access to a Confidential AKS cluster (`az aks get-credentials` command). [Learn more on how to configure credentials or create new Azure Confidential Computing-enabled AKS clusters](https://docs.microsoft.com/en-us/azure/confidential-computing/confidential-nodes-aks-get-started). We suggest node sizes `Standard_DC2s_v2` and bigger - with 3 nodes in the nodepool for used in the demo.
2. Deploy Scone LAS to your Kubernetes cluster.
3. Get access to the PySpark base image used in this demo from Scone's Container Registry: `registry.scontain.com:5050/clenimar/pyspark:5.5.0-amd-experimental-k8s` - see [instructions here](https://sconedocs.github.io/SCONE_Curated_Images/).

**An example of the pre-requisite setup - PowerShell:**
```powershell
# 1. Configure kubectl access to a Confidential AKS Cluster
az account set --subscription "your--subscription--name"
$rg = "your--rg--name"
$k8s = "your--aks--name" 

# Create RG
az group create --name $rg --location EastUS

# Create AKS cluster with System Node Pool
az aks create -g $rg --name $k8s --node-count 1 --ssh-key-value 'ssh-rsa AAAAB3Nza...==' --enable-addon confcom

# Create Confidential Node Pool - 1 Confidential Node
az aks nodepool add --cluster-name $k8s --name confcompool1 -g $rg --node-vm-size Standard_DC4s_v2 --node-count 1

# Grab kubeconfig from AKS
az aks get-credentials -g $rg --name $k8s

# Prep kubectl
kubectl config get-contexts
kubectl config use-context $k8s
kubectl get nodes

# Should see something like this
# NAME                                   STATUS   ROLES   AGE     VERSION
# aks-confcompool1-42230234-vmss000000   Ready    agent   49s     v1.20.7
# aks-nodepool1-42230234-vmss000000      Ready    agent   4h33m   v1.20.7

# 2. Deploy Scone LAS to your Kubernetes cluster.
kubectl apply -f kubernetes/scone-las.yaml

# 3. Get access to PySpark base image from Scone's Container Registry, build and push to your Container Registry that AKS has access to - e.g. ACR

# Login to Scone's container registry (after receiving access to Gitlab)
docker login registry.scontain.com:5050 -u your--scone--gitlab--username -p your--scone--gitlab--password

# Pull PySpark Container image
docker pull registry.scontain.com:5050/clenimar/pyspark:5.5.0-amd-experimental-k8s

# Create ACR and login
$acr = $k8s + "acr"
az acr create -g $rg --name $acr --sku Basic
az acr login --name $acr

# Image pull secret for Kubernetes
# AAD Service Principal creating secret (can use new/existing - doesn't matter)
$SERVICE_PRINCIPAL_ID="your--sp--clientid"
$SERVICE_PRINCIPAL_SECRET="your--sp--clientpassword"

# Assign Service Principal to ACR with image pull permissions
$ACR_REGISTRY_ID=$(az acr show -g $rg --name $acr --query id --output tsv)
az role assignment create --assignee $SERVICE_PRINCIPAL_ID --scope $ACR_REGISTRY_ID --role acrpull

# Create Kubernetes Image secret in default namespace
kubectl create secret docker-registry acrsecret `
					    --namespace default `
					    --docker-server="$acr.azurecr.io" `
					    --docker-username=$SERVICE_PRINCIPAL_ID `
					    --docker-password=$SERVICE_PRINCIPAL_SECRET
```

**Execute steps - bash**

```bash
# Change to directory with this repo
cd "/mnt/c/Users/your--username/My Documents/GitHub/sgx-pyspark-sql-demo"

# Build and push image: The image must be pushed to a Container Registry accessible from the Kubernetes Cluster
export ACR=aiasconfconeaksacr
export DRIVER_IMAGE=$ACR.azurecr.io/pyspark-scone-driver:5.5.0
docker build . -t $DRIVER_IMAGE -f driver.Dockerfile

export EXEC_IMAGE=$ACR.azurecr.io/pyspark-scone-exec:5.5.0
docker build . -t $EXEC_IMAGE -f executor.Dockerfile

# Push image to ACR
az acr login --name $ACR
docker push $DRIVER_IMAGE
docker push $EXEC_IMAGE

# We use the same SCONE image as the client (for consistency, also because it has spark-submit available etc.), 
# We mount the Kubernetes credentials from our local into the container.

# Path where kubeconfig is stored in your environment
export KUBECONFIG_DIR=/mnt/c/Users/your--username/.kube

# Run client container environment
docker run -it --rm --entrypoint bash -v $KUBECONFIG_DIR:/root/.kube -e DRIVER_IMAGE=$DRIVER_IMAGE -e EXEC_IMAGE=$EXEC_IMAGE -e SCONE_MODE=sim $DRIVER_IMAGE

# -------------- Inside pyspark-scone:5.5.0 Container --------------
# Ensure accessibility to K8s cluster
kubectl get nodes

# Setup RBAC for Spark in Kubernetes
kubectl apply -f /fspf/kubernetes/rbac.yaml

# Gather the kubernetes master node's address, for spark-submit
export MASTER_ADDRESS=$(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}')

# Export key and tag for the encrypted executors. This will allow the SCONE runtime
# to transparently decrypt the encrypted source code. These variables are securely injected
# by SCONE CAS after remote attestation.
export SCONE_FSPF_KEY=$(cat /fspf/keytag.txt | awk '{print $11}')
export SCONE_FSPF_TAG=$(cat /fspf/keytag.txt | awk '{print $9}')

# Attestation-specific env. vars. which will be used in the Scone session templates.
# CAS_NAMESPACE is a random CAS namespace to store our policies.
# PYSPARK_SESSION_NAME is the name of our Scone session.
# MAA_PROVIDER is the Microsoft Azure Attestation provider we're using to attest our applications.
# NOTE: Skip if running in simulated mode (remote attestation is only supported in hardware mode).
export CAS_NAMESPACE="pyspark-azure-$RANDOM$RANDOM"
export PYSPARK_SESSION_NAME="pyspark"
export MAA_PROVIDER="https://dataownerccmpv0.eus.attest.azure.net"
envsubst '$CAS_NAMESPACE' < /fspf/policies/namespace.yaml.template > /fspf/policies/namespace.yaml
envsubst '$CAS_NAMESPACE $PYSPARK_SESSION_NAME $MAA_PROVIDER $SCONE_FSPF_KEY $SCONE_FSPF_TAG' < /fspf/policies/pyspark.yaml.template > /fspf/policies/pyspark.yaml

# Confirm values in the Scone session for PySpark.
cat /fspf/policies/pyspark.yaml

# Submit Scone session to CAS. In this demo we're using a Public CAS provided by Scone for
# testing and demo purposes only. More information: https://sconedocs.github.io/public-CAS/
# 1. Attest Public CAS to make sure it has the expected enclave measurement.
scone cas attest 5-5-0.scone-cas.cf 783c797f68cc700afdc3067c02a4fcf77ec01f4f880debb5c0ce36bd866e794b -GCS --only_for_testing-debug --only_for_testing-ignore-signer
# 2. Create our namespace.
scone session create /fspf/policies/namespace.yaml
# 3. Create our session.
scone session create /fspf/policies/pyspark.yaml
# Now that we created the Scone session, we have to let the application
# know which session to request when starting up. We do that via the following env. vars:
export SCONE_CAS_ADDR="5-5-0.scone-cas.cf"
export SCONE_CONFIG_ID="$CAS_NAMESPACE/$PYSPARK_SESSION_NAME/nyc-taxi-yellow"

# Generate the properties file from properties.template 
# envsubst will replace $IMAGE, $SCONE_CAS_ADDR and $SCONE_CONFIG_ID.

# NOTE: If running on non-SGX nodes (i.e., in simulated mode), adjust the properties file accordingly:
# - remove the property `spark.kubernetes.executor.podTemplateFile`
# - remove the property `spark.kubernetes.driver.podTemplateFile`
# - remove the property `spark.kubernetes.driverEnv.SCONE_CAS_ADDR`
# - remove the property `spark.kubernetes.driverEnv.SCONE_CONFIG_ID`
# - remove the property `spark.executorEnv.SCONE_CAS_ADDR`
# - remove the property `spark.executorEnv.SCONE_CONFIG_ID`
# - add property `spark.kubernetes.driverEnv.SCONE_MODE sim`
#
# Simulated mode does not support Remote Attestation, so we inject
# key and tag for the encrypted driver/executors podsdirectly.
# - add property `spark.kubernetes.driverEnv.SCONE_FSPF /fspf/encrypted-files/volume.fspf`
# - add property `spark.kubernetes.driverEnv.SCONE_FSPF_KEY $SCONE_FSPF_KEY`
# - add property `spark.kubernetes.driverEnv.SCONE_FSPF_TAG $SCONE_FSPF_TAG`
envsubst < /fspf/properties.template > /fspf/properties

# Since we are using images held in ACR, add
# `spark.kubernetes.container.image.pullSecrets $SECRET_NAME` to properties file.
echo 'spark.kubernetes.container.image.pullSecrets acrsecret' >> properties

# Confirm values in the properties file
cat properties

# Submit job to the cluster.
spark-submit --master k8s://$MASTER_ADDRESS --deploy-mode cluster --name nyc-taxi-yellow --properties-file /fspf/properties local:///fspf/encrypted-files/nyc-taxi-yellow.py

# The driver pod will spawn the executor pod(s), and clean up after they're finished.
# Once the job is finished, the driver pod will be kept in Completed state.

# Spark logs will be displayed in the driver pod - follow by substituting the name of your driver pod:
kubectl logs nyc-taxi-yellow-...-driver --follow # Run this outside the container to see logs in real-time
```

Scone also supports the fine-tuning of its runtime performance through a configuration file, where one can configure the number of queues and threads to better suit the workload needs. For example, workloads that execute more system calls (e.g., I/O-intensive) tend to benefit from having more application threads (called _ethreads_), or to have them pinned to specific CPU cores to avoid core switching. [Learn more about Scone runtime configuration](https://sconedocs.github.io/SCONE_ENV/).
