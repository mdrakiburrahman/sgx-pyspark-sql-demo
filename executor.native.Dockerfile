FROM clenimar/pyspark:3.1.2-native

USER root

ADD input/libraries/* /opt/spark/jars/

RUN apt update && apt install python3 -y

ENTRYPOINT [ "/opt/spark/entrypoint.sh" ]
