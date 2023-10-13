FROM alpine:3.18.4

RUN addgroup -S production_group && adduser -S prodUser -G production_group


COPY /app /app

COPY template.conf /conf.toml
COPY main.py /main.py
COPY pyproject.toml /
COPY poetry.lock /

RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev openssh-client curl && \
    curl -sSL https://install.python-poetry.org | POETRY_HOME=/etc/poetry python3 - && \
    apk del --no-cache --purge gcc musl-dev 
    # python3-dev libffi-dev

ENV PATH="/etc/poetry/bin:${PATH}"

RUN poetry config virtualenvs.create false --local
RUN chmod +r /poetry.toml

RUN poetry install
USER prodUser

ENV port 8000
ENV host "0.0.0.0"

ENV debug false
ENV encryption_on true

ENV api_key ""
ENV secret_key ""
ENV cluster_url ""
ENV encryption_key ""

CMD poetry run python3 main.py