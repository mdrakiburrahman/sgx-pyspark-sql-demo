# Confidential Data Analytics with Apache Spark on Intel SGX Confidential Containers

## Overview

This repository demonstrates the following architecture for **Confidential Data Analytics** on Azure Intel SGX enabled Confidential Virtual machines (**AKS** or **Standalone**) for running containerized applications: <br>

> 💡 Confidential data analytics in this context is meant to imply: **_"run analytics on PII data with peace of mind against data exfiltration"_** - this includes potential `root`-level access breach both internally (rogue admin) or externally (system compromise).
> Confidential data analytics helps meet your high security and confidentiality needs by removing the untrusted parties from computation like cloud operator, service/guest admins. This execution helps meet your data compliance needs.

![Architecture Diagram](images/Architecture-Diagram.png)

### Goal

Demonstrate how to run **end-to-end Confidential Data Analytics** on Azure (presumably on PII/trade sensistive data), leveraging [Azure SQL Always Encrypted with Secure Enclaves](https://docs.microsoft.com/en-us/sql/relational-databases/security/encryption/always-encrypted-enclaves?view=sql-server-ver15) as the database, and containerized **Apache Spark** on [Intel SGX-enabled Azure machines](https://docs.microsoft.com/en-us/azure/confidential-computing/confidential-computing-enclaves) for analytics workloads.

## Live Demo

[![SCONE: Secure Linux Containers with Intel SGX](https://img.youtube.com/vi/em6ovuznAf8/0.jpg)](https://youtu.be/em6ovuznAf8)

### Key points

- **Azure DC Series**: We run a containerized [Spark 3.1.1](https://spark.apache.org/releases/spark-release-3-1-1.html) application, on an [**Azure DC4s_v3**](https://docs.microsoft.com/en-us/azure/virtual-machines/dcv3-series) machine running Docker. These machines are backed by the latest generation of Intel XEON Scalabe Processor with large Encrypted Page Cache (EPC) memory sizes. These Azure Virtual Machines include the [Intel SGX extensions](https://software.intel.com/content/www/us/en/develop/topics/software-guard-extensions.html) - the **_key component_** to enabling the core message of this demo.
  - **💡 Note**: This demo works identically well on [AKS running DC4s_v3 nodes](https://docs.microsoft.com/en-us/azure/confidential-computing/confidential-computing-enclaves). We perform the demo on the standalone node to enjoy the additional benefits of RDP for demonstrations purposes that `kubectl` wouldn't allow as easily.
- **SCONE**: To run Spark inside an Intel SGX enclave - we leverage [SCONE](https://docs.microsoft.com/en-us/azure/confidential-computing/confidential-containers#scone-scontain), who have essentially taken the [Open Source Spark code](https://sconedocs.github.io/sconeapps_spark/), and wrapped it with their enclave runtime so that Spark can run inside SGX enclaves (a task that requires deep knowledge of the SGX ecosystem - something SCONE is an expert at).
> 💡 Please note that SCONE (Scontain UG) is an Azure partner in confidential computing space who enables easy support to existing docker containers on Intel SGX Enclaves. You can also choose from other OSS and partners from [here](https://docs.microsoft.com/en-us/azure/confidential-computing/confidential-containers).

   - **Sconedocs**: Scone's official documentation for Azure integration and getting started: [link](https://sconedocs.github.io/aks/)

### Pre-requisites

1. Registry for access to the 2 Spark images used per scenario:
   - `#TODO`
2. Follow the tutorial here to deploy an Azure SQL Always Encrypted with Secure Enclaves Database with some sample PII data: [link](https://docs.microsoft.com/en-us/azure/azure-sql/database/always-encrypted-enclaves-getting-started)
3. A **DC4s_v3** VM deployment (standalone or in AKS cluster)
   - **Scenario 1** (baseline) can run on any machine (local of Azure VM non-confidential) (including the DC4s_v3 machine).
   - **Scenario 2** will not work without Intel SGX enabled machines - i.e. must run on an Azure DC series machine. You can enable [xfce](https://www.xfce.org/) to get an RDP interface.

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

In this scenario, we leverage Spark with Scone on a [Confidential Capable AKS cluster](https://docs.microsoft.com/en-us/azure/confidential-computing/confidential-nodes-aks-get-started) to process larger datasets in a distributed fashion. The Dataset we use is the common [NYC Taxi](https://docs.microsoft.com/en-us/azure/open-datasets/dataset-taxi-yellow?tabs=pyspark) Dataset - where we demonstrate a simple Spark Job ([`COUNT *`](https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.sql.DataFrame.count.html)) on 1.5 Billion Rows of Parquet files (50 GB) stored on Azure Blob Storage:

> Azure Confidential Enclave VM's [DCsv3 and DCdsv3](https://docs.microsoft.com/en-us/azure/virtual-machines/dcv3-series) is in public preview and offers large EPC memeory sizes to help run memory intensive applications like analytics.

![Scenario 3](images/Scenario-3.png)

The tasks are divided among the available executors (user configurable), which allows for horizontal scalability. The executors are written in Python and have their source code encrypted by the Scone filesystem protection features we've already discussed.

### A note about EPC Memory Size

The same protection guarantees as the previous scenarios apply here too. Kubernetes admins, or any privileged user, cannot inspect the in-memory contents or source code of driver or executors. EPC is specialized memeory partition in an Azure Confidential Enclaves VM that Enclaves or Confidential containers use. These VM's also come with regulay memory (un-encrypted) memeory to run non-enclave apps. As part of this sample we did performance [benchmarking](#benchmark) and did not see any noticable performance drops).

### Running with Remote Attestation

Remote attestation ensures that your workload has not been tampered with when deployed to a untrusted host, such as a VM instance or a Kubernetes node that runs on the cloud. In this process, attestation evidence provided by Intel SGX hardware is analyzed by an attestation provider. To perform remote attestation on a Scone application (such as Spark driver and executor pods), two services are required:

- **Local Attestation Service (LAS)**: runs on the untrusted host and gathers the attestation evidence provided by Intel SGX about the application being attested. This evidence is signed and forwarded to CAS; and
- **Configuration and Attestation Service (CAS)**: a central service that manages security policies (called **Scone _sessions_**), configuration and secrets. CAS compares the attestation evidence gathered by LAS against the application's security policies (defined by the application owner) to decide whether the enclave is trustworthy of not. If so, CAS allows the enclave to run and securely injects configuration and secrets into it. [Learn more about CAS and its features, such as secret generation and access control](https://sconedocs.github.io/CASOverview/).

> 💡 The decision of whether the attestation evidence is trustworthy or not can be delegated to a third-party attestation provider, such as Intel Attestation Service or Microsoft Azure Attestation.

For this scenario, we use a [Public CAS](https://sconedocs.github.io/public-CAS/) provided by Scone for test purposes. In production scenarios you will control your own CAS - which also runs inside of enclaves and can be remotely attested.

#### Pre-requisite Setup

1. Configure `kubectl` access to a Confidential AKS cluster (`az aks get-credentials` command). [Learn more on how to configure credentials or create new Azure Confidential Computing-enabled AKS clusters](https://docs.microsoft.com/en-us/azure/confidential-computing/confidential-nodes-aks-get-started). We suggest node sizes `Standard_DC4s_v3` and bigger - with 3 nodes in the nodepool for used in the demo.
2. Deploy Scone LAS to your Kubernetes cluster.
3. Get access to the PySpark base image used in this demo from Scone's Container Registry: `registry.scontain.com:5050/clenimar/pyspark:5.6.0plus` - see [instructions here](https://sconedocs.github.io/SCONE_Curated_Images/).

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
docker pull registry.scontain.com:5050/clenimar/pyspark:5.6.0plus

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

# Build the confidential Spark image.
# The image must be pushed to a Container Registry accessible from the Kubernetes Cluster.
export ACR=aiasconfconeaksacr
export SPARK_IMAGE=$ACR.azurecr.io/pyspark-scone:5.6.0
./build-spark-image.sh

# Source the needed environment variables generated by the build script.
# The directory "build" is created by the build script and stores build resources
# for the encrypted Spark images (such as properties, SCONE policies and metadata).
source build/env.sh

# Push image to ACR.
az acr login --name $ACR
docker push $SPARK_IMAGE

# Configure remote attestation and submit your SCONE policies.
# Specify your SCONE CAS[1] address and MrEnclave.
# In this example, we use a public CAS instance[2] for testing purposes.
# [1] https://sconedocs.github.io/CASOverview/
# [2] https://sconedocs.github.io/public-CAS/
export SCONE_CAS_ADDR="5-6-0.scone-cas.cf"
export SCONE_CAS_MRENCLAVE="0902eec722b3de0d11b56aab3671cc8540e62bd2333427780c8a9cd855e4f298"

# If running with Microsoft Azure Attestation policy, export the MAA provider URL.
# NOTE: You need to edit "security.attestation" section of "policies/pyspark.hw.yaml.template" to enable MAA.
# NOTE: MAA is not supported in simulated mode (i.e., on hardware without SGX support).
export MAA_PROVIDER="https://sharedeus.eus.attest.azure.net"

# Attest SCONE CAS.
docker run --rm -t \
  -e SCONE_CLI_CONFIG=/cas/config.json \
  -v $PWD/build/cas:/cas \
  --entrypoint bash \
  $SPARK_IMAGE -c "scone cas attest $SCONE_CAS_ADDR $SCONE_CAS_MRENCLAVE -GCS --only_for_testing-debug --only_for_testing-ignore-signer"

# Create your CAS namespace from the template and submit it.
envsubst '$CAS_NAMESPACE' < policies/namespace.yaml.template > build/policies/namespace.yaml
docker run --rm -t \
  -e SCONE_CLI_CONFIG=/cas/config.json \
  -v $PWD/build/cas:/cas \
  -v $PWD/build/policies:/policies \
  --entrypoint bash \
  $SPARK_IMAGE -c "scone session create /policies/namespace.yaml"

# Create your SCONE policy for Spark drivers and executors from the template and submit it.
# NOTE: If running in simulated mode (i.e., on hardware without SGX support), use "policies/pyspark.sim.yaml.template" instead.
envsubst '$SCONE_CAS_ADDR $CAS_NAMESPACE $PYSPARK_SESSION_NAME $DRIVER_MAIN_FSPF_KEY $DRIVER_MAIN_FSPF_TAG $DRIVER_VOLUME_FSPF_KEY $DRIVER_VOLUME_FSPF_TAG $DRIVER_JAVA_MRENCLAVE $DRIVER_PYTHON_MRENCLAVE $EXECUTOR_JAVA_MRENCLAVE' < policies/pyspark.hw.yaml.template > build/policies/pyspark.yaml
docker run --rm -t \
  -e SCONE_CLI_CONFIG=/cas/config.json \
  -v $PWD/build/cas:/cas \
  -v $PWD/build/policies:/policies \
  --entrypoint bash \
  $SPARK_IMAGE -c "scone session create /policies/pyspark.yaml"

export SCONE_CONFIG_ID="$CAS_NAMESPACE/$PYSPARK_SESSION_NAME/nyc-taxi-yellow"

# Generate your Spark properties file from the template.
# NOTE: If running in simulated mode (i.e., on hardware without SGX support), use "properties.sim.template" instead.
envsubst < properties.hw.template > build/properties

# Since we are using images held in ACR, add
# `spark.kubernetes.container.image.pullSecrets $SECRET_NAME` to properties file.
echo 'spark.kubernetes.container.image.pullSecrets acrsecret' >> build/properties

# Submit RBAC policies to your Kubernetes cluster, if not already.
kubectl apply -f kubernetes/rbac.yaml

# Retrieve the Kubernetes master IP address to use in the spark-submit command.
MASTER_ADDRESS=$(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}')

# Copy the pod template to provide SGX to Spark driver and executors.
# NOTE: If running in simulated mode (i.e., on hardware without SGX support), use "kubernetes/sim-sgx-pod-template.yaml" instead.
cp kubernetes/hw-sgx-pod-template.yaml build/kubernetes

# Submit the Spark job with spark-submit. We use a vanilla Spark image (without SGX support) for simplicity.
# Note that the submission step takes place on the local machine. The job to be executed on the remote cluster,
# which is potentially untrusted, runs entirely inside of SGX enclaves.
# We mount the Kubernetes credentials from our local environment into the Spark client container.
# Path where kubeconfig is stored in your environment.
export KUBECONFIG_DIR=/mnt/c/Users/your--username/.kube

# Confirm values in the Spark properties file. You can customize parameters such as executor count.
cat build/properties

# Submit the job.
docker run -it --rm \
  -v $KUBECONFIG_DIR:/root/.kube \
  -v $(pwd)/build:/build godatadriven/pyspark:3.1 --master k8s://$MASTER_ADDRESS --deploy-mode cluster --name nyc-taxi-yellow --properties-file /build/properties local:///fspf/encrypted-files/nyc-taxi-yellow.py

# The driver pod will spawn the executor pod(s), and clean up after they're finished.
# Once the job is finished, the driver pod will be kept in Completed state.

# Spark logs will be displayed in the driver pod - follow by substituting the name of your driver pod:
kubectl logs nyc-taxi-yellow-...-driver --follow # Run this outside the container to see logs in real-time
```

### Benchmark

To assess performance of Spark with Scone, we compare Scone against a vanilla PySpark (e,g, a regular [Bitnami image](https://hub.docker.com/r/bitnami/spark/tags?page=1&ordering=last_updated) with no SGX support) image for the same aggregation on a large dataset stored in Azure Blob Storage. For our benchmark, we use the [NYC Taxi (Yellow)](https://docs.microsoft.com/en-us/azure/open-datasets/dataset-taxi-yellow) dataset, which has approximately 1.5 billion rows and 50 GB. The reader is encouraged to try this on even larger datasets - similar results should follow.

**Workload:**

- Spark job performs a `df.count()` on the dataset, which returns the total number of rows. In Scone scenarios, the workload (drivers/executors) have their Python code encrypted.

Scenarios:

| Scenario | Description |
| :-: | - |
| **Vanilla (Intel/no SGX)** | Baseline. The driver and the executors are in plain text and run on Intel CPUs without SGX support using vanilla PySpark images |
| **Scone (AMD/simulated mode)** | The driver and the executors are encrypted and run on AMD CPUs. Scone simulates an SGX enclave by creating encrypted memory regions |
| **Scone (Intel/hardware mode)** | The driver and the executors are encrypted and run on Intel CPUs with SGX support, benefitting from all hardware-backed security guarantees provided by Intel SGX and Scone |


Clusters:

| Scenario | Cluster | Node size | Cores; RAM | SGX EPC memory | Region |
| :-: | :-: | :-: | :-: | :-: | :-: |
| **Vanilla (Intel/no SGX)** | Intel | [Standard_D4s_v4](https://docs.microsoft.com/en-us/azure/virtual-machines/dv4-dsv4-series) | 4 vCPUs; 16 GB | - | us-east |
 **Scone (AMD/simulated mode)** | AMD | [Standard_D4a_v4](https://docs.microsoft.com/en-us/azure/virtual-machines/dav4-dasv4-series#dav4-series) | 4 vCPUs; 16 GB | - | us-east |
**Scone (Intel/hardware mode)** | Intel | [Standard_DC4ds_v3](https://docs.microsoft.com/en-us/azure/virtual-machines/dcv3-series) | 4 CPUs; 32 GB (this includes SGX EPC memory) | 16 GB | us-east2 |


- All scenarios run on AKS clusters.
- The dataset is located in `us-east` region.
- All Pods (driver or executor) have the same CPU and memory requests/limits in Kubernetes.
- We run one executor per cluster node.
- The results below are the mean of each configuration. We use a repetition factor of 3.

Results:

![Scone PySpark on AKS](images/Scone-PySpark-on-AKS.png)

The results show that Scone PySpark is able to run PySpark applications in a distributed fashion, being able to horizontally scale the workload across multiple Spark executors for a simple aggregation over a large dataset. Even though the aggregation itself is simple (`df.count()`), it shows that having a dataset much larger (50 GB) than the container memory limits (**10 GB**), enclave sizes (**1 GB** for Python processes and **4 GB** for Java processes) and SGX EPC memory (**16 GB** for [DC4ds_v3](https://docs.microsoft.com/en-us/azure/virtual-machines/dcv3-series)) is not a practical bottleneck. Furthermore, Scone scenarios have their driver/executor code encrypted.

It's also important to notice that the overhead in execution time observed for Scone scenarios (hardware mode or simulated mode) compared to Vanilla PySpark image corresponds to the **enclave startup process**. This process takes a fixed amount of time given an enclave size. Therefore, for applications that are more complex and take longer to complete, this overhead should correspond to a small fraction of the overall execution time.

Scone also supports the fine-tuning of its runtime performance through a configuration file, where one can configure the number of queues and threads to better suit the workload needs. For example, workloads that execute more system calls (e.g., I/O-intensive) tend to benefit from having more application threads (called _ethreads_), or to have them pinned to specific CPU cores to avoid core switching. [Learn more about Scone runtime configuration](https://sconedocs.github.io/SCONE_ENV/).
