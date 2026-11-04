# Base images are pinned by digest so Dependabot can raise a PR for each
# rebuild of the tag. Change both FROM lines together.
FROM python:3.10-slim-bullseye@sha256:f1fb49e4d5501ac93d0ca519fb7ee6250842245aba8612926a46a0832a1ed089 AS clone

ARG CDCS_REPO
ARG BRANCH
# Optional: exact commit of $BRANCH to build, for reproducible images
ARG CDCS_COMMIT

# Install git
RUN apt-get update && apt-get install -y git

# Clone git repository
RUN git clone -b $BRANCH $CDCS_REPO /tmp/repo && \
    if [ -n "$CDCS_COMMIT" ]; then git -C /tmp/repo checkout --detach "$CDCS_COMMIT"; fi

FROM python:3.10-slim-bullseye@sha256:f1fb49e4d5501ac93d0ca519fb7ee6250842245aba8612926a46a0832a1ed089 AS build
LABEL maintainer="National Institute of Standards and Technology"

ARG PROJECT_NAME
ARG PIP_CONF

# Directory in container for project source files
ENV DOCKYARD_SRVPROJ="/srv/curator"

# Copy cloned cdcs repository
COPY --from=clone /tmp/repo $DOCKYARD_SRVPROJ

# Install necessary packages
RUN apt-get update && apt-get --no-install-recommends install -y \
    netcat python g++ gcc dnsutils gettext \
    libxml2-dev libxslt-dev python-dev zlib1g libssl-dev \
    python3-pip libpq-dev postgresql-client xmlsec1 \
    && rm -rf /var/lib/apt/lists/*

# Setup pip
RUN mkdir -p /root/.config/pip
COPY pip/$PIP_CONF/pip.conf /root/.config/pip

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
