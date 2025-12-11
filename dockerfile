FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install only chromium as it is used in the code
RUN playwright install chromium

COPY main.py ./
COPY kakalot_scraper/ kakalot_scraper/

COPY healthcheck.sh .

RUN chmod +x healthcheck.sh

RUN touch /app/build_info.txt
RUN echo "Build completed at $(date)" > /app/build_info.txt

ENTRYPOINT ["python", "main.py", "--self-service"]
