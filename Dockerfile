# Documentation:
#   - https://docs.astral.sh/uv/guides/integration/docker/
#   - https://hynek.me/articles/docker-uv/

FROM python:3.12 AS build

ENV LANG=C.UTF-8
ENV TZ=Europe/Copenhagen

WORKDIR /src

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_LINT_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/app/.venv

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    SETUPTOOLS_SCM_PRETEND_VERSION=1 \
    uv sync --locked --no-dev --no-install-project

COPY . /src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable

FROM python:3.12

LABEL maintainer="Daniel Mizsak"
LABEL org.opencontainers.image.source="https://github.com/daniel-mizsak/linker"

ENV LANG=C.UTF-8
ENV TZ=Europe/Copenhagen

WORKDIR /app

COPY asgi.py /app/asgi.py

COPY --from=build /app /app
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 80
CMD ["uvicorn", "asgi:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]
