| Site           | Branch  | Status                                                                                                                                                         |
| -------------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| RCA Staging    | staging | [![CircleCI](https://circleci.com/gh/torchbox/rca-wagtail-2019/tree/staging.svg?style=shield)](https://circleci.com/gh/torchbox/rca-wagtail-2019/tree/staging) |
| RCA Production | master  | [![CircleCI](https://circleci.com/gh/torchbox/rca-wagtail-2019/tree/master.svg?style=shield)](https://circleci.com/gh/torchbox/rca-wagtail-2019/tree/master)   |

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

This repository includes a Vagrantfile for running the project in a Debian VM and
a fabfile for running common commands with Fabric.

To set up a new build:

```bash
git clone https://github.com/torchbox/rca-wagtail-2019.git
cd rca
vagrant up
vagrant ssh
```

Then within the SSH session:

```bash
dj migrate
dj createcachetable
dj createsuperuser
djrun
```

This will make the site available on the host machine at: http://127.0.0.1:8000/

# Front-end assets

To build front-end assets you will additionally need to run the following commands:

```bash
npm install
npm run build:prod
```

After any change to the CSS or Javascript you will need to run the build command again, either in the vm or on your host machine. See the [Front-end tooling docs](docs/front-end-tooling.md) for further details.

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
