FROM alpine:3.20.3 as builder

RUN adduser --disabled-password --gecos "" productionUser

# these steps are combined to shrink down the size of the image, because removing the
# dependencys from another run command dosent really have an effect.
RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev curl openssh git

RUN mkdir -p /root/.ssh && \
    touch /root/.ssh/known_hosts && \
    ssh-keyscan -t rsa central-perk01.prosper.edge >> /root/.ssh/known_hosts

USER productionUser
ENV HOME /home/productionUser
ENV PATH="/home/productionUser/.local/bin:${PATH}"

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

COPY /app /app

COPY main.py /main.py
COPY pyproject.toml /
COPY poetry.lock /

RUN poetry install --no-dev --no-root

FROM alpine:3.20.3
RUN adduser --disabled-password --gecos "" productionUser
COPY /app /app

COPY main.py /main.py

RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python

ENV HOME /home/productionUser
COPY --from=builder /home/productionUser/.cache/ ${HOME}/productionVirtualEnv

USER productionUser

ENV port=8000
ENV host="0.0.0.0"

ENV debug=false
ENV encryption_on=true

ENV api_key=""
ENV secret_key=""
ENV cluster_url=""
ENV encryption_key=""


CMD /home/productionUser/productionVirtualEnv/pypoetry/virtualenvs/*/bin/python3 main.py



# FROM alpine:3.18.4

# RUN addgroup -S production_group && adduser -S prodUser -G production_group


# COPY /app /app

# COPY template.conf /conf.toml
# COPY main.py /main.py
# COPY pyproject.toml /
# COPY poetry.lock /

# RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev curl && \
#     curl -sSL https://install.python-poetry.org | POETRY_HOME=/etc/poetry python3 - && \
#     apk del --no-cache --purge gcc musl-dev libffi-dev
#     # python3-dev

# ENV PATH="/etc/poetry/bin:${PATH}"

# RUN poetry config virtualenvs.create false --local
# RUN chmod +r /poetry.toml

# RUN poetry install
# USER prodUser

# ENV port 8000
# ENV host "0.0.0.0"

# ENV debug false
# ENV encryption_on true

# ENV api_key ""
# ENV secret_key ""
# ENV cluster_url ""
# ENV encryption_key ""

# CMD poetry run python3 main.py
