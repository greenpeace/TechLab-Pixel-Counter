# Dockerfile
FROM python:3.9
RUN apt-get update -y
RUN apt-get install -y python3-pip python-dev build-essential

WORKDIR /app

COPY . /app

ENV PYTHONUNBUFFERED=1 \
    GOOGLE_APPLICATION_CREDENTIALS=key.json \
    GCP_PROJECT="social-climate-tech"

RUN pip install -r requirements.txt

# Expose port 8080
EXPOSE 8080

ENTRYPOINT ["python"]
CMD ["app.py"]
# End of Dockerfile