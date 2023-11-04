FROM node:20-alpine3.18 AS builder

WORKDIR /build

COPY web /build

RUN npm i
RUN npm run build

FROM python:3.11.6

WORKDIR /app

COPY mappacker/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY mappacker /app/mappacker
COPY main.py /app

COPY --from=builder /build/dist /app/static

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--workers", "1"]