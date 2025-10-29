FROM python:3.12-slim

ENV PYTHONUNBUFFERED True
ENV PATH="$PATH:/usr/src/app/.local/bin"

RUN apt-get update && apt-get upgrade -y && apt-get install -y curl

RUN groupadd -r app && useradd -r -g app -d /usr/src/app app

WORKDIR /app

RUN python3 -m pip install --upgrade pip
COPY quality-rules/ quality-rules
RUN pip install --no-cache-dir -r quality-rules/requirements.txt

USER app

HEALTHCHECK --interval=1m --timeout=10s CMD curl --fail http://localhost:$PORT/health || exit 1

CMD python3 -m fastapi run quality-rules/main.py --port $PORT
