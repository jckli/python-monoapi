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

RUN sed -i "s/'arm' in platform.processor().lower()/'arm' in platform.processor().lower() or 'aarch64' in platform.machine().lower()/" src/socketify/native.py

WORKDIR /build/socketify.py/src/socketify/native

RUN CFLAGS="-Wno-error=stringop-overflow" make linux PLATFORM=aarch64

WORKDIR /build/socketify.py

RUN pip install wheel && python3 setup.py bdist_wheel

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
