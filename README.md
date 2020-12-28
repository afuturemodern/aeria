# aeria

[![GitHub Project](https://img.shields.io/badge/GitHub--blue?style=social&logo=GitHub)](https://github.com/afuturemodern/aeria)
[![GitHub Actions Status: CI](https://github.com/afuturemodern/aeria/workflows/CI/badge.svg?branch=master)](https://github.com/afuturemodern/aeria/actions?query=workflow%3ACI+branch%3Amaster)
[![Code Coverage](https://codecov.io/gh/afuturemodern/aeria/graph/badge.svg?branch=master)](https://codecov.io/gh/afuturemodern/aeria?branch=master)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Visualized social web explorer


## Using

From Applications directory, run

```
python -m neo4j.cloudchaser
```

## Installation

In a fresh virtual environment, you can install from the master branch of the GitHub repository:

```
$ python -m pip install "git+https://github.com/afuturemodern/aeria.git"
```

The above is actually cloning and installing directly from the Git repository.

However, if you want to, you can of course also install it directly from the Git repository "locally" by first cloning the repo and then from the top level of it running

```
$ python -m pip install .
```

### Setting up Neo4j DB

Assuming that one has finished running the `soundcloud_api_wrapper.ipynb` to get a `profile.graphml` file...

Docker is preferred here. Quickly one-liner:

```
sudo docker run --rm --name neo4j \
                -p7474:7474 -p7687:7687 \
                --env NEO4J_AUTH=neo4j/admin \
                --env NEO4JLABS_PLUGINS='["apoc"]' \
                --env NEO4J_apoc_import_file_enabled=true \
                -v $(PWD)/profile.graphml:/var/lib/neo4j/import/profile.graphml \
                neo4j:4.1
```

This:

  * runs `neo4j @ 4.1-latest`
  * exposes the ports `7474` and `7687` locally on your computer (host)
  * sets username/password to `neo4j`/`admin`
  * adds the `APOC` plugin
  * tells `apoc` that we want to enable file import from `/var/lib/neo4j/import` folder
  * mounts the saved `profile.graphml` into the `/var/lib/neo4j/import` folder of the docker image for importing

Note, the `7474` port is useful for opening up the `neo4j` browser at http://localhost:7474/browser/. We can (in another shell) tell the running docker container to import our `profile.graphml`:

```
docker exec neo4j cypher-shell -u neo4j -p admin "CALL apoc.import.graphml('profile.graphml', {})"
```

which will import it into the database for us. Then one can just browser or use neo4j for exploring.

## Contributing

As this library is experimental contributions of all forms are welcome.

If you have ideas on how to improve the API or fix a bug please open an Issue.

You are of course also most welcome and encouraged to open PRs.

### Developing

To develop, use a virtual environment.

Once the environment is activated, clone the repo from GitHub

```
git clone git@github.com:afuturemodern/aeria.git
```

and install all necessary packages for development

```
python -m pip install --ignore-installed --upgrade -e .[complete]
```

(Optional) Then setup the Git pre-commit hooks by running

```
pre-commit install
```
