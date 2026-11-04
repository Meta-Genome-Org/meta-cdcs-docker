# Base images are pinned by digest so Dependabot can raise a PR for each
# rebuild of the tag. Change both FROM lines together. Debian 12: bullseye's
# security archive started returning 404s after its LTS ended (2026-08).
FROM python:3.11-slim-bookworm@sha256:94a8fee35252d06ab75856f15f12c7bae67b10e8a6da93c7fded82b2610926cd AS clone

ARG CDCS_REPO
ARG BRANCH
# Optional: exact commit of $BRANCH to build, for reproducible images
ARG CDCS_COMMIT

# Install git
RUN apt-get update && apt-get install -y git

# Clone git repository
RUN git clone -b $BRANCH $CDCS_REPO /tmp/repo && \
    if [ -n "$CDCS_COMMIT" ]; then git -C /tmp/repo checkout --detach "$CDCS_COMMIT"; fi

FROM python:3.11-slim-bookworm@sha256:94a8fee35252d06ab75856f15f12c7bae67b10e8a6da93c7fded82b2610926cd AS build
LABEL maintainer="National Institute of Standards and Technology"

ARG PROJECT_NAME
ARG PIP_CONF

# Directory in container for project source files
ENV DOCKYARD_SRVPROJ="/srv/curator"

# Copy cloned cdcs repository
COPY --from=clone /tmp/repo $DOCKYARD_SRVPROJ

# Install necessary packages
RUN apt-get update && apt-get --no-install-recommends install -y \
    g++ python3-dev gcc gettext  \
    libxml2-dev libxslt-dev zlib1g libssl-dev \
    python3-pip libpq-dev postgresql-client xmlsec1 \
    && rm -rf /var/lib/apt/lists/*

# Setup pip
RUN mkdir -p /root/.config/pip
COPY pip/$PIP_CONF/pip.conf /root/.config/pip
RUN pip install --upgrade pip

# Pin every Python package to a known-good version. meta-mdcs leaves Django,
# celery and others unpinned, so without this a rebuild is an upgrade.
COPY ./constraints.txt /etc/pip-constraints.txt
ENV PIP_CONSTRAINT=/etc/pip-constraints.txt

# Install additional python packages
RUN pip install psycopg2 uwsgi gunicorn[gthread]

# Install requirements
WORKDIR $DOCKYARD_SRVPROJ
RUN pip install -r requirements.txt
RUN pip install -r requirements.core.txt

# Get entrypoint ready for the image
COPY ./gunicorn.conf.py /etc
COPY ./docker-entrypoint*.sh /
COPY ./scripts /scripts
RUN chmod a+x /docker-entrypoint*.sh /scripts/*

# Create folder for uwsgi socket, static files, media files
RUN mkdir /tmp/curator $DOCKYARD_SRVPROJ/static.prod $DOCKYARD_SRVPROJ/media

# Create unprivileged user
RUN groupadd cdcs && \
    adduser cdcs --disabled-password --gecos '' --ingroup cdcs  && \
    chown -R cdcs:cdcs $DOCKYARD_SRVPROJ /tmp/curator

USER cdcs

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["curator", "uwsgi"]
