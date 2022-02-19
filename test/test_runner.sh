#!/bin/bash

set -e

if command -v python3;  then
  export PYTHON=python3
  mkdir -p /usr/local/lib/python3.6/site-packages
else
  export PYTHON=python2
fi;

make install

if grep -q -i 'release 5' /etc/redhat-release; then
  python ./test/unittest_suite.py
else
  make test
fi

if [ ${PYTHON} = "python3" ]; then
  # don't fail on flake8 for now
  ${PYTHON} -m flake8 --ignore E501 src/ || true
fi

if [ ${PYTHON} = "python2" ]; then
  for binary in bin/*; do
    if [[ "${binary}" = "bin/katello-tracer-upload" ]] && ! rpm -q python2-tracer --quiet; then
      continue;
    fi;
    python -- ${binary} -f ;
    python -- ${binary} -help ;
  done
fi;
