ARG TARGETPLATFORM
ARG TARGETARCH

FROM --platform=$BUILDPLATFORM python:3.13-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake libuv1-dev libz-dev git golang && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /build
RUN git clone --recursive https://github.com/cirospaciari/socketify.py.git
WORKDIR /build/socketify.py

RUN sed -i "s/is_aarch64 = 'aarch64' in platform.machine().lower()/import os\\nis_arm = os.environ.get('TARGETARCH') == 'arm64'/" src/socketify/builder.py && \
    sed -i "/is_arm = 'arm' in platform.processor().lower() or is_aarch64/d" src/socketify/builder.py && \
    sed -i "s/\('arm' in platform.processor().lower()\)/(\1 or 'aarch64' in platform.machine().lower() or 'arm64' in platform.machine().lower())/" \
        src/socketify/native.py

WORKDIR /build/socketify.py/src/socketify/native
RUN case "$TARGETARCH" in \
       arm64) CFLAGS="-Wno-error=stringop-overflow" make linux PLATFORM=aarch64 ;; \
       amd64) make linux ;; \
       *) echo "Unsupported arch: $TARGETARCH" && exit 1 ;; \
    esac

WORKDIR /build/socketify.py
RUN pip install --upgrade pip wheel setuptools && \
    TARGETARCH=$TARGETARCH python3 setup.py bdist_wheel

FROM --platform=$TARGETPLATFORM python:3.13-slim

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libuv1 zlib1g && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN if grep -q "socketify" requirements.txt; then sed -i "/socketify/d" requirements.txt; fi
RUN pip install --no-cache-dir -r requirements.txt

COPY --from=builder /build/socketify.py/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl

# App
COPY . .
EXPOSE 3000
CMD ["python", "main.py", "--host", "0.0.0.0", "--port", "3000"]
