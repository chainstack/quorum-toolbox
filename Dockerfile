FROM chainstack/orch-runtime-docker:latest

# Version 10 Dec 2019

COPY . /app

WORKDIR /app

RUN python setup.py develop

CMD ["./quorumtoolbox/tests/test_all.sh"]
