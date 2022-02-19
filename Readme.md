# katello-host-tools

This repository is a collection of software tools which are useful for [clients of Katello](https://theforeman.org/plugins/katello/nightly/installation/clients.html). It supports errata and package profile reporting across a number of different rpm based platforms.

## Run

```
make install
katello-enabled-repos-upload
```

#### With Docker

```sh
make docker-run

# In the container shell:
make install
katello-enabled-repos-upload
```

## Test

Full test suites:

```sh
make test
```

#### Manually

```sh
./test/unittest_suite.py # run all the tests
python -m unittest test.test_yum_plugins.test_enabled_repos_upload # run a specific test module
python -m unittest test.test_yum_plugins.test_enabled_repos_upload.TestSendEnabledReport.test_send # run a specific test
```

Optionally, work from the test's directory:

```sh
cd test/test_yum_plugins
python -m unittest test_enabled_repos_upload # run a specific test module
python -m unittest test_enabled_repos_upload.TestSendEnabledReport.test_send # run a specific test
```

#### With Docker

Full suite:

```sh
make docker-test # run test/test_runner.sh in a container and exit
```

Single tests:
```sh
make docker-run # open a bash shell in a container

# In the container shell:
make install
# use manual test commands above
```

## Contribute

Please, open your PR and join our [community](https://theforeman.org/contribute.html)!

Issues tracked via [Redmine](https://projects.theforeman.org/projects/katello/).
