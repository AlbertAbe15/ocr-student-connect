FROM python:3.11.6

WORKDIR /usr/src/app

ENV http_proxy http://ITS-587159-e97f3:d8cdf@proxy.its.ac.id:8080
ENV https_proxy https://ITS-587159-e97f3:d8cdf@proxy.its.ac.id:8080

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
