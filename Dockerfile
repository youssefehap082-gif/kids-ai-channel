FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y     ffmpeg     imagemagick     git     && rm -rf /var/lib/apt/lists/*

# Fix ImageMagick policy for MoviePy
RUN sed -i 's/none/read,write/g' /etc/ImageMagick-6/policy.xml

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "scripts/pipeline_runner.py"]
