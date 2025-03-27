FROM python:3.10 AS base
WORKDIR /bot

ARG bot_token
ARG chat_id

ENV bot_token=${bot_token}
ENV chat_id=${chat_id}

COPY pyproject.toml pyproject.toml
COPY config config
COPY src src
COPY resources resources
COPY config.json config.json

FROM base AS test

COPY tests tests

RUN pip install .[dev]

WORKDIR /bot

ENTRYPOINT [ "pytest" ]

FROM base AS prod

RUN pip install .

WORKDIR /bot
ENTRYPOINT [ "run_bot" ]

