FROM registry.scontain.com:5050/clenimar/pyspark:5.5.0-amd-experimental-k8s-jvm

USER root

ADD input/libraries/* /spark/jars/

ENTRYPOINT [ "/opt/entrypoint.sh" ]
