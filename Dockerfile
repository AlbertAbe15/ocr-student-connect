# Use ARG to define the proxy variables so they can be passed at build time
ARG HTTP_PROXY=http://<proxy>
ARG HTTPS_PROXY=https://<proxy>
ARG FTP_PROXY=ftp://<proxy>
ARG SOCKS_PROXY=socks:<proxy>

FROM python:3.11.6

WORKDIR /usr/src/app

# Set environment variables for the proxy inside the image
ENV http_proxy=$HTTP_PROXY \
    https_proxy=$HTTPS_PROXY \
    ftp_proxy=$FTP_PROXY \
    socks_proxy=$SOCKS_PROXY

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgl1-mesa-glx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY . ./
RUN set -ex \
    && apt-get update \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get install -y poppler-utils \
    && apt-get install -y tesseract-ocr

# Command to run the application
EXPOSE 5000
CMD ["python", "./app.py"]
