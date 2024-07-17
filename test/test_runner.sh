#!/bin/bash

set -e

if command -v python3;  then
  export PYTHON=python3
  VENV="${PYTHON} -m venv"
else
  export PYTHON=python2
  VENV="virtualenv"
fi;

${VENV} --system-site-packages ./venv
. ./venv/bin/activate

make install

make test

if [ ${PYTHON} = "python3" ]; then
  # don't fail on flake8 for now
  ${PYTHON} -m flake8 --ignore E501 src/ || true
fi

if [ ${PYTHON} = "python2" ]; then
  for binary in katello-enabled-repos-upload katello-package-upload katello-tracer-upload ; do
    if [[ "${binary}" = "katello-tracer-upload" ]] && ! rpm -q python2-tracer --quiet; then
      continue;
    fi;
    ${binary} -f
    ${binary} -help
  done
fi;
