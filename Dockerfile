FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.5.4 /uv /usr/local/bin/uv

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project
COPY mtgprices ./mtgprices
RUN uv sync --frozen --no-dev

RUN useradd --create-home --uid 1000 app && mkdir /data && chown app /data
USER app
ENV MTGPRICES_DATA_DIR=/data
VOLUME /data
EXPOSE 8000

# Внутри контейнера сервер слушает 0.0.0.0. Пароль задаётся через MTGPRICES_PASSWORD;
# без пароля публикуйте порт только на этот компьютер: -p 127.0.0.1:8000:8000
CMD ["/app/.venv/bin/mtgprices", "--host", "0.0.0.0", "--no-browser", "--no-password"]
