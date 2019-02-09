FROM chainstack/orch-runtime-docker:latest

# Version 4 Dec 2018
ARG ISTANBUL_VERSION=1.0.1

# Install istanbul
RUN wget -q https://github.com/chainstack/quorum-docker/releases/download/v.2.2.1/istanbul_v${ISTANBUL_VERSION}_linux_amd64.tar.gz -O - \
    | tar xzO istanbul> /usr/local/bin/istanbul \
	&& chmod +x /usr/local/bin/istanbul

COPY . /app

WORKDIR /app

RUN python setup.py develop

CMD ["./quorumtoolbox/tests/test_all.sh"]

