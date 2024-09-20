# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .

RUN pip install poetry
RUN poetry install
RUN ls -la

# Instalar wget, unzip, curl, gnupg, ffmpeg e outras dependências necessárias para o Chrome
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Adicionar a chave pública do Google para Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -

# Adicionar o repositório do Google Chrome
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

# Atualizar e instalar o Google Chrome
RUN apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Baixar e instalar o ChromeDriver
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}') \
    && echo "Google Chrome version: $CHROME_VERSION" \
    && wget -O /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chromedriver-linux64.zip \
    && unzip -j /tmp/chromedriver.zip "chromedriver-linux64/chromedriver" -d /usr/local/bin \
    && rm /tmp/chromedriver.zip

# Definir variável de ambiente para o ChromeDriver
ENV PATH="/usr/local/bin/chromedriver:${PATH}"

COPY app .

# Comando para rodar o script Python
CMD ["poetry", "run", "python", "main.py"]