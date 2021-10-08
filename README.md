[![CircleCI prod](https://circleci.com/gh/torchbox/rca-wagtail-2019/tree/master.svg?style=shield)](https://circleci.com/gh/torchbox/rca-wagtail-2019/tree/master)
[![codecov](https://codecov.io/gh/torchbox/rca-wagtail-2019/branch/master/graph/badge.svg?token=GBDM9H1A2X)](https://codecov.io/gh/torchbox/rca-wagtail-2019)
[![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# RCA Wagtail 2019

## Technical documentation

This project contains technical documentation written in Markdown in the `/docs` folder.

You can view it using `mkdocs` by running:

```bash
mkdocs serve
```

The documentation will be available at: http://localhost:8001/

## Contributing

1. Make changes on a new branch, including a broad category and the ticket number if relevant e.g. `feature/123-extra-squiggles`, `fix/newsletter-signup`.
2. Push your branch to the remote.
3. Make merge requests at e.g. https://github.com/torchbox/rca-wagtail-2019, no trailing slash/merge_requests/new, setting the 'Source branch' to your feature branch and the 'Target branch' to `master`. Select 'Compare branches and continue'.
4. Edit details as necessary.

Gitlab has built-in CI tests. These can be configured by editing `.gitlab-ci.yml`. By default these are run on all pushes and merge requests.

If you need to preview work on `staging`, this can be merged and deployed manually without making a merge request. You can still make the merge request as above, but add a note to say that this is on `staging`, and not yet ready to be merged to `master`.

### Code styleguide

This project’s code formatting is enforced with [Prettier](https://prettier.io/) for supported languages. Make sure to have Prettier integrated with your editor to auto-format when saving files, or to manually run it before committing (`npm run format`).

## Automatic linting locally

You can also run the linting tests automatically before committing. This is optional. It uses pre-commit, which is installed by default in the vagrant box, and a .pre-commit-config.yml file is included for the project.

To use when making commits on your host machine you must install pre-commit, either create a virtualenv to use with the project, or to install globally see instructions at (https://pre-commit.com/#install).

Pre-commit will not run by default. To set it up, run `pre-commit install` inside the Vagrant box, or on the host if you have installed pre-commit there.

# Setting up a local build

This repository includes `docker-compose` configuration for running the project in local Docker containers,
and a fabfile for provisioning and managing this.

## Dependencies

The following are required to run the local environment. The minimum versions specified are confirmed to be working:
if you have older versions already installed they _may_ work, but are not guaranteed to do so.

- [Docker](https://www.docker.com/), version 19.0.0 or up
  - [Docker Desktop for Mac](https://hub.docker.com/editions/community/docker-ce-desktop-mac) installer
  - [Docker Engine for Linux](https://hub.docker.com/search?q=&type=edition&offering=community&sort=updated_at&order=desc&operating_system=linux) installers
- [Docker Compose](https://docs.docker.com/compose/), version 1.24.0 or up
  - [Install instructions](https://docs.docker.com/compose/install/) (Linux-only: Compose is already installed for Mac users as part of Docker Desktop.)
- [Fabric](https://www.fabfile.org/), version 2.4.0 or up
  - [Install instructions](https://www.fabfile.org/installing.html)
- Python, version 3.6.9 or up

Note that on Mac OS, if you have an older version of fabric installed, you may need to uninstall the old one and then install the new version with pip3:

```bash
pip uninstall fabric
pip3 install fabric
```

You can manage different python versions by setting up `pyenv`: https://realpython.com/intro-to-pyenv/

## Running the local build for the first time

If you are using Docker Desktop, ensure the Resources:File Sharing settings allow the cloned directory to be mounted in the web container (avoiding `mounting` OCI runtime failures at the end of the build step).

Starting a local build can be done by running:

```bash
git clone https://github.com/torchbox/rca-wagtail-2019
cd rca
fab build
fab start
fab sh
```

Then within the SSH session:

```bash
dj migrate
dj createcachetable
dj createsuperuser
djrun
```

The site should be available on the host machine at: http://127.0.0.1:8000/

### Frontend tooling

Here are the common commands:

```bash
# Install front-end dependencies.
npm install
# Start the Webpack build in watch mode, without live-reload.
npm run start
# Start the Webpack server build on port 3000 only with live-reload.
npm run start:reload
# Do a one-off Webpack development build.
npm run build
# Do a one-off Webpack production build.
npm run build:prod
```

There are two ways to run the frontend tooling:

- In Docker. This is the default, most portable and secure, but much slower on macOS. Running `fab start` will start a `frontend` container. Use `fab sh --service frontend` in a separate terminal to SSH into the container. Then run npm commands within this new SSH session. `exit` once you’re done.
- Or run npm commands from a terminal on your local machine. Create a `.env` file in the project root (see `.env.example`) with `FRONTEND=local`. `fab start` will no longer start a `frontend` container.

## Installing python packages

Python packages can be installed using `poetry` in the web container:

```
fab sh
poetry add wagtail-guide
```

To reset installed dependencies back to how they are in the `poetry.lock` file:

```
fab sh
poetry install --no-root
```

## Deployment

The static assets should be automatically generated on deployment and you do
not need to commit them. The command used to generate the production version
of static files is `npm run build:prod`.

# Servers

VM should come preinstalled with Fabric, Heroku CLI and AWS CLI.

## Login to Heroku

Please log in to Heroku before executing any commands for servers hosted there
using the `heroku login -i` command. You have to do it both in the VM and your
host machine if you want to be able to use it in both places.

## Pulling data

To populate your local database with the content of staging/production:

```bash
fab pull-staging-data
fab pull-production-data
```

To fetch images and other media:

```bash
fab pull-staging-media
fab pull-production-media
```

To fetch only original images, with no extra media files and no renditions:

```bash
fab pull-staging-images
fab pull-production-images
```

## Data anonymisation

[Django birdbath](https://pypi.org/project/django-birdbath/) is being used to anonymise data locally. Ensure you have exported the following variables into the VM:

```
export ALLOWS_ANONYMISATION='rca-staging'
export HEROKU_APP_NAME='rca-staging'
```

After pulling data, the cli will show a warning about birdbath needing to run. Which you should do.

Birdbath is on by default, set in settings/base.py and is turned off on live environments using environment variables.

## Deployments

Deployments to stage are automatically handled by CircleCI.

For production, CircleCI requires manual approval, this is done over at the [CircleCI Workflows for master](https://circleci.com/gh/torchbox/workflows/rca-wagtail-2019/tree/master). A job awaiting approval will show as 'pending'. Manual approval consists of clicking on the pending tasks and clicking 'approve'.

## Connect to the shell

To open the shell of the servers.

```bash
fab staging-shell
fab production-shell
```

## Pushing database and media files

Please be aware executing those commands is a possibly destructive action. Make
sure to take backups.

If you want to push your local database to the servers.

```bash
fab push-staging-data
fab push-production-data
```

Or if you want to push your local media files.

```bash
fab push-staging-media
fab push-production-media
```
