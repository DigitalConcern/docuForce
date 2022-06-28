FROM python:3.10

# Allows docker to cache installed dependencies between builds
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

EXPOSE 8001
COPY ../../../Изображения/Camera%20Roll/docuForce ./app
# runs the production server
RUN chmod +x /app/docker-entry.sh
ENTRYPOINT ["/app/docker-entry.sh"]