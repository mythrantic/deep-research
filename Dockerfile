
FROM python:3.13-slim

# Install curl and the Azure CLI
RUN apt-get update && apt-get install -y \
    curl \
    apt-transport-https \
    git \
    lsb-release \
    gnupg \
    && curl -sL https://aka.ms/InstallAzureCLIDeb | bash \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


RUN pip install --no-cache-dir uv

WORKDIR /app
COPY . /app

RUN uv pip install --system --no-cache .

EXPOSE 8000

CMD ["uv", "run", "python", "src/server.py"]
