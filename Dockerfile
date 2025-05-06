FROM eclipse-temurin:19-jdk-jammy

WORKDIR /app

# Install Python 3.12
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.12 python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache -r requirements.txt

COPY MiniGo/src/antlr-4.9.2-complete.jar ./MiniGo/src/

COPY . .

ENV ANTLR_JAR="/app/MiniGo/src/antlr-4.9.2-complete.jar"

CMD ["bash"]