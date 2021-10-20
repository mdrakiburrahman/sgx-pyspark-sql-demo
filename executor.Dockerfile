FROM registry.scontain.com:5050/clenimar/pyspark:5.6.0-jvm

USER root

ADD input/libraries/* /spark/jars/

ENV SCONE_LOG=ERROR

ENTRYPOINT [ "/opt/entrypoint.sh" ]
