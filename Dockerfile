ARG TARGETPLATFORM
ARG TARGETARCH

FROM --platform=$TARGETPLATFORM python:3.13-slim AS builder
ENV DEBIAN_FRONTEND=noninteractive PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake libuv1-dev libz-dev git golang ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /build
RUN git clone --recursive https://github.com/cirospaciari/socketify.py.git
WORKDIR /build/socketify.py

RUN test -f src/socketify/native.py && \
    sed -i "s/\('arm' in platform.processor().lower()\)/(\1 or 'aarch64' in platform.machine().lower() or 'arm64' in platform.machine().lower())/" \
        src/socketify/native.py

WORKDIR /build/socketify.py/src/socketify/native
RUN case "$TARGETARCH" in \
      arm64) CFLAGS="-Wno-error=stringop-overflow" make linux PLATFORM=aarch64 ;; \
      amd64) make linux ;; \
      *) echo "Unsupported arch: $TARGETARCH" && exit 1 ;; \
    esac

WORKDIR /build/socketify.py
RUN python -m pip install --upgrade pip wheel setuptools && \
    python setup.py bdist_wheel

RUN set -eux; \
    ARCH_TAG=$([ "$TARGETARCH" = "arm64" ] && echo "aarch64" || echo "x86_64"); \
    ls -l dist/*${ARCH_TAG}*.whl

FROM --platform=$TARGETPLATFORM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends libuv1 zlib1g && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN if grep -qiE '^\s*socketify' requirements.txt; then sed -i -e "/^\s*socketify/Id" requirements.txt; fi && \
    pip install --no-cache-dir -r requirements.txt

COPY --from=builder /build/socketify.py/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl

COPY . .

EXPOSE 3000
CMD ["python", "main.py", "--host", "0.0.0.0", "--port", "3000"]

