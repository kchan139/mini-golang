# Stage 1

FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache -r requirements.txt

# Stage 2

FROM python:3.12-slim

# Install Java Runtime Environment (JRE)
RUN apt-get update && \
    apt-get install -y --no-install-recommends default-jre && \
    # Clean up apt cache
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/

COPY MiniGo/src/antlr-4.9.2-complete.jar ./MiniGo/src/

COPY . .

ENV ANTLR_JAR="/app/MiniGo/src/antlr-4.9.2-complete.jar"

CMD ["bash"] 