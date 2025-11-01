FROM node:22-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    chromium \
    locales \
    && rm -rf /var/lib/apt/lists/*

# Set up Spanish locale for the bot
RUN sed -i '/es_ES.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen es_ES.UTF-8

ENV LANG es_ES.UTF-8
ENV LANGUAGE es_ES:es
ENV LC_ALL es_ES.UTF-8

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY package*.json ./

# Skip Chromium download since we're using system Chromium
ENV PUPPETEER_SKIP_DOWNLOAD=true
RUN npm ci --only=production

COPY bot.py .
COPY messages.py .
COPY renderer.js .

RUN mkdir -p data/images data/images-new

# Create a non-root user to run the application
RUN useradd -m -u 1000 botuser && \
    chown -R botuser:botuser /app

USER botuser

# Configure Puppeteer to use system Chromium
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

CMD ["python3", "bot.py"]
