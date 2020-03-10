FROM chainstack/orch-runtime-docker:latest

COPY . /app

WORKDIR /app

RUN python setup.py develop

CMD ["./quorumtoolbox/tests/test_all.sh"]
