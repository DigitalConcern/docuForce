FROM python:3.10

# Allows docker to cache installed dependencies between builds
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

EXPOSE 8001
COPY . ./wapp
# runs the production server
RUN chmod +x /wapp/docker-entry.sh
ENTRYPOINT ["/wapp/docker-entry.sh"]