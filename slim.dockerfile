FROM us-docker.pkg.dev/fif-corp-cl-misc-prod/fif-gaiaops-hardenized-prod/secaas/python:3.12

ENV PYTHONUNBUFFERED True
ENV PATH="$PATH:/usr/src/app/.local/bin"

USER root
RUN apk update
RUN apk upgrade --no-cache

RUN addgroup -S app && adduser -S -G app -h /usr/src/app app

WORKDIR /app

RUN python3 -m pip install --upgrade pip
COPY quality-rules/ quality-rules
RUN pip install --no-cache-dir -r quality-rules/requirements.txt

USER app

HEALTHCHECK --interval=1m --timeout=10s CMD curl --fail http://localhost:$PORT/health || exit 1

CMD python3 -m fastapi run quality-rules/main.py --port $PORT