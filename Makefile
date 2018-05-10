USE_SELINUX=$(shell test -d /sys/fs/selinux && echo ":Z")
DOCKERFILE  ?= $(CURDIR)/images/Dockerfile.el7
PYTHON ?= python2

install:
	cd src/ && $(PYTHON) setup.py install

test-python3:
	pip3 install -r test-requirements.txt --user
	python3 ./test/unittest_suite.py

test-python2:
	pip install -r test-requirements.txt --user
	python2 test/unittest_suite.py

docker-run:
	docker build -f $(DOCKERFILE) -t kht-builder .
	docker run -it --volume $(CURDIR):/app$(USE_SELINUX) kht-builder /bin/bash

docker-test:
	docker build -t kht-builder -f $(DOCKERFILE) .
	docker run -it --volume $(CURDIR):/app$(USE_SELINUX) kht-builder /bin/bash ./test/test_runner.sh
