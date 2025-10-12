FROM python:3.12 as builder

RUN apt-get update && apt-get install -y build-essential cmake libuv1-dev libz-dev git golang ca-certificates libatomic1

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir --no-binary :all: -r requirements.txt

RUN echo "--- Verifying built library for ARM ---"
RUN ls -l /usr/local/lib/python3.12/site-packages/socketify/

FROM python:3.12-slim

RUN apt-get update && apt-get install -y libatomic1 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .

EXPOSE 3000
CMD ["python", "main.py"]
