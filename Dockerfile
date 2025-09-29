FROM python:3.13-rc-slim as builder

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libuv1-dev \
	libz-dev \
    git \
	golang \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /build

RUN git clone --recursive https://github.com/cirospaciari/socketify.py.git

WORKDIR /build/socketify.py

ARG TARGETARCH
RUN if [ "$TARGETARCH" = "arm64" ]; then \
      LIB_NAME="libsocketify_linux_arm64.so"; \
    else \
      LIB_NAME="libsocketify_linux_amd64.so"; \
    fi && \
    echo 'from pathlib import Path' > src/socketify/native.py && \
    echo 'from ._socketify import ffi' >> src/socketify/native.py && \
    echo "library_path = str(Path(__file__).parent / \"$LIB_NAME\")" >> src/socketify/native.py && \
    echo "lib = ffi.dlopen(library_path)" >> src/socketify/native.py

WORKDIR /build/socketify.py/src/socketify/native

ARG TARGETARCH
RUN if [ "$TARGETARCH" = "arm64" ]; then \
      CFLAGS="-Wno-error=stringop-overflow" make linux PLATFORM=aarch64; \
    else \
      make linux; \
    fi


WORKDIR /build/socketify.py

RUN pip install wheel setuptools && python3 setup.py bdist_wheel

FROM ghcr.io/astral-sh/uv:python3.13-alpine

WORKDIR /app

RUN apk add --no-cache libuv gcompat

COPY requirements.txt .

RUN if grep -q "socketify" requirements.txt; then sed -i "/socketify/d" requirements.txt; fi

RUN uv pip install -r requirements.txt --system

COPY --from=builder /build/socketify.py/dist/*.whl .

RUN uv pip install *.whl --system && rm *.whl

COPY . .

EXPOSE 3000

CMD ["uv", "run", "main.py", "--host", "0.0.0.0", "--port", "3000"]
