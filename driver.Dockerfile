FROM registry.scontain.com:5050/clenimar/pyspark:5.6.0

USER root

# Install kubectl. This is just for convenience reasons, since we use
# the container itself as a client.
RUN apk add --update curl vim \
    && curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

WORKDIR /fspf

# Copy application code and libraries.
ADD . .
ADD input/libraries/* /spark/jars/

# Dos2Unix Cleanup - required for Windows Users running Bash
RUN for f in *.sh; do dos2unix $f; chmod u+r+x $f; done

# Encrypt the executor code with SCONE FSPF.
# NOTE: We can't access the SGX driver from within the
# Docker build context, so set SCONE_MODE=sim.
RUN SCONE_MODE=sim /fspf/fspf.sh

ENV SCONE_LOG=ERROR

ENTRYPOINT [ "/opt/entrypoint.sh" ]
