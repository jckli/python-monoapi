FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

COPY requirements.txt .

RUN uv pip sync --system requirements.txt

COPY . .

EXPOSE 3000

CMD ["uv", "run", "main:app"]
