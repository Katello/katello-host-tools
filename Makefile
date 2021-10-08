RHEL5=$(shell grep -q -i 'release 5' /etc/redhat-release 2>/dev/null || false)
PYTHON3=$(shell which python3 && which pip3)
USE_SELINUX=$(shell test -d /sys/fs/selinux && echo ":Z")
DOCKERFILE  ?= $(CURDIR)/images/Dockerfile.el7
DIST=$(shell echo $(DOCKERFILE) | tr "." "\n" | tail -1 | tr '[:upper:]' '[:lower:]')
IMAGE ?= kht-builder-$(DIST)
ifneq ($(PYTHON3),)
PYTHON ?= python3
PIP ?= pip3
else
PYTHON ?= python
PIP ?= pip
endif

PODMAN=$(shell which podman)
ifneq ($(PODMAN),)
CONTAINER_EXEC ?= podman
else
CONTAINER_EXEC ?= docker
endif

default: help

help:
	@echo "Usage: make [target] <ARG=value, ...>"
	@echo
	@echo "target:"
	@echo "  help          show this message"
	@echo "  install       install locally with default python"
	@echo "  test-install  install test requirements"
	@echo "  test          test locally"
	@echo "  docker-build  build the docker image"
	@echo "  docker-run    run bash in a preconfigured docker container"
	@echo "  docker-test   test in a docker container"
	@echo
	@echo "python args:"
	@echo "  PYTHON        python executable to use (python2, python3)"
	@echo "  PIP           pip executable to use (pip, pip3)"
	@echo
	@echo "docker-* args:"
	@echo "  DOCKERFILE    dockerfile to use (one of images/Dockerfile.*)"

install:
	cd src/ && $(PYTHON) setup.py install

test-install:
ifeq ($(RHEL5),) # no pip for RHEL5
	$(PIP) install -r test-requirements.txt --user
endif

test: test-install
	$(PYTHON) test/unittest_suite.py

docker-build:
	$(CONTAINER_EXEC) build -f $(DOCKERFILE) -t $(IMAGE) .

docker-run: docker-build
	$(CONTAINER_EXEC) run --rm -itv $(CURDIR):/app$(USE_SELINUX) $(IMAGE) bash

docker-test: docker-build
	$(CONTAINER_EXEC) run --rm -v $(CURDIR):/app$(USE_SELINUX) $(IMAGE) ./test/test_runner.sh

docker-clean:
	$(CONTAINER_EXEC) image rm $(IMAGE)
