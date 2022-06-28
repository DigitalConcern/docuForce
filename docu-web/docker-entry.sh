#!/bin/sh

echo "Migrate the Database at startup of project"

python /app/source/manage.py makemigrations
python /app/source/manage.py migrate

echo "Django docker is fully configured successfully."

python /app/source/main.py