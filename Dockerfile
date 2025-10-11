FROM python:3.12 as builder

RUN apt-get update && apt-get install -y build-essential cmake libuv1-dev libz-dev git golang ca-certificates 

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir --no-binary socketify -r requirements.txt

FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY . .

EXPOSE 3000
CMD ["python", "main.py"]
