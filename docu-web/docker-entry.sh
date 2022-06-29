#!/bin/sh

echo "Migrate the Database at startup of project"

python /wapp/source/manage.py makemigrations
python /wapp/source/manage.py migrate

echo "Django docker is fully configured successfully."

python /wapp/source/main.py