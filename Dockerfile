# Keep in sync with: the astral-sh/uv-pre-commit rev in .pre-commit-config.yaml,
# and the astral-sh/setup-uv `version` input in .github/workflows/test.yaml and
# lint.yaml.
ARG UV_VERSION=0.13.9

# (Keep the version in sync with the node install below)
FROM node:26 AS frontend

# Make build & post-install scripts behave as if we were in a CI environment (e.g. for logging verbosity purposes).
ARG CI=true

ARG COREPACK_VERSION=0.36.0
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

# package.json is needed here already: with no version given, `corepack
# prepare` reads the pnpm version+hash to install from its "packageManager"
# field, so that field stays the only place the pin lives.
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml .babelrc.js webpack.config.js ./

# node:26 ships no corepack at all, so install the resolved corepack release
# first, then let it activate the pnpm release package.json pins.
RUN npm install -g "corepack@${COREPACK_VERSION}" \
    && corepack enable pnpm \
    && corepack prepare --activate

# Install front-end dependencies.
RUN pnpm install --frozen-lockfile

# Compile static files
COPY ./rca/static_src/ ./rca/static_src/
RUN pnpm run build:prod


# We use Debian images because they are considered more stable than the alpine
# ones becase they use a different C compiler. Debian images also come with
# all useful packages required for image manipulation out of the box. They
# however weight a lot, approx. up to 1.5GiB per built image.
FROM ghcr.io/astral-sh/uv:${UV_VERSION}@sha256:d3b601f0c7b118bc1753febf7c41cc80981df678445e0254284eecf84db79a7d AS uv-binary

FROM python:3.15-trixie AS production

ARG UV_SYNC_ARGS="--no-dev"

# Install dependencies in a virtualenv
ENV VIRTUAL_ENV=/venv

RUN useradd rca --create-home && mkdir /app $VIRTUAL_ENV && chown -R rca /app $VIRTUAL_ENV

WORKDIR /app

# Set default environment variables. They are used at build time and runtime.
# If you specify your own environment variables on Heroku or Dokku, they will
# override the ones set here. The ones below serve as sane defaults only.
#  * PATH - Make sure our venv is on the PATH.
#  * PYTHONUNBUFFERED - This is useful so Python does not hold any messages
#    from being output.
#    https://docs.python.org/3.11/using/cmdline.html#envvar-PYTHONUNBUFFERED
#    https://docs.python.org/3.11/using/cmdline.html#cmdoption-u
#  * DJANGO_SETTINGS_MODULE - default settings used in the container.
#  * PORT - default port used. Please match with EXPOSE so it works on Dokku.
#    Heroku will ignore EXPOSE and only set PORT variable. PORT variable is
#    read/used by Gunicorn.
#  * WEB_CONCURRENCY - number of workers used by Gunicorn. The variable is
#    read by Gunicorn.
#  * GUNICORN_CMD_ARGS - additional arguments to be passed to Gunicorn. This
#    variable is read by Gunicorn
ENV PATH=$VIRTUAL_ENV/bin:$PATH \
    UV_SYNC_ARGS=${UV_SYNC_ARGS} \
    UV_PROJECT_ENVIRONMENT=$VIRTUAL_ENV \
    UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=rca.settings.production \
    PORT=8000 \
    WEB_CONCURRENCY=3 \
    GUNICORN_CMD_ARGS="-c gunicorn-conf.py --max-requests 1200 --max-requests-jitter 50 --access-logfile - --timeout 25"

# Make $BUILD_ENV available at runtime
ARG BUILD_ENV
ENV BUILD_ENV=${BUILD_ENV}

# Port exposed by this container. Should default to the port used by your WSGI
# server (Gunicorn). This is read by Dokku only. Heroku will ignore this.
EXPOSE 8000

RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    git \
    && apt-get autoremove && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=uv-binary /uv /usr/local/bin/uv

# Don't use the root user as it's an anti-pattern and Heroku does not run
# containers as root either.
# https://devcenter.heroku.com/articles/container-registry-and-runtime#dockerfile-commands-and-runtime
USER rca

# Install your app's Python requirements.
COPY --chown=rca pyproject.toml uv.lock ./
RUN uv sync --locked ${UV_SYNC_ARGS} --extra gunicorn --no-install-project && rm -rf $HOME/.cache

COPY --chown=rca --from=frontend ./rca/static_compiled ./rca/static_compiled

# Copy application code.
COPY --chown=rca . .

# Run uv sync again to install our project (so the rca package is always importable)
RUN uv sync --locked ${UV_SYNC_ARGS} --extra gunicorn

# Collect static. This command will move static files from application
# directories and "static_compiled" folder to the main static directory that
# will be served by the WSGI server.
RUN SECRET_KEY=none python manage.py collectstatic --noinput --clear

# Load shortcuts
COPY ./docker/bashrc.sh /home/rca/.bashrc

# Run the WSGI server. It reads GUNICORN_CMD_ARGS, PORT and WEB_CONCURRENCY
# environment variable hence we don't specify a lot options below.
CMD gunicorn rca.wsgi:application

# These steps won't be run on production
FROM production AS dev

# Swap user, so the following tasks can be run as root
USER root

# Install `psql`, useful for `manage.py dbshell`
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    postgresql-client \
    && apt-get autoremove && rm -rf /var/lib/apt/lists/*

# Restore user
USER rca

# Install nvm and node/npm
ARG NVM_VERSION=0.40.4
COPY --chown=rca .nvmrc ./
RUN curl https://raw.githubusercontent.com/nvm-sh/nvm/v${NVM_VERSION}/install.sh | bash \
    && bash --login -c "nvm install --no-progress && nvm alias default $(nvm run --silent --version)"

# Enable corepack and prepare pnpm for the nvm-installed node above (which,
# like node:26, ships no corepack at all), and run it once so its platform
# binary is downloaded now rather than on every `pnpm` invocation. With no
# version given, `corepack prepare` reads the pin from package.json's
# "packageManager" field (already present from the production stage's
# `COPY --chown=rca . .` above), so that field stays the only place it lives.
ARG COREPACK_VERSION=0.36.0
# node_modules below is installed in the frontend stage and used from another
# path here, so pnpm's pre-run dependency check would reinstall it before
# every `pnpm run`. It comes from the frozen lockfile, so turn the check off.
ENV pnpm_config_verify_deps_before_run=false
RUN bash --login -c "npm install -g corepack@${COREPACK_VERSION} \
    && corepack enable pnpm \
    && corepack prepare --activate \
    && pnpm --version"

# Pull in the node modules for the frontend
COPY --chown=rca --from=frontend ./node_modules ./node_modules

# do nothing forever - exec commands elsewhere
CMD tail -f /dev/null
