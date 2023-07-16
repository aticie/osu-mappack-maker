FROM node:20-alpine3.18 AS builder

WORKDIR /build

COPY ./web /build

RUN npm i
RUN npm run build

FROM python:3.11

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./main.py /app/main.py
COPY --from=builder /build/dist /app/static

ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]