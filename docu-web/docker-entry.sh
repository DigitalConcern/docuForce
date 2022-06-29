#!/bin/sh

echo "Migrate the Database at startup of project"

python /wapp/source/manage.py makemigrations

python /wapp/source/manage.py migrate

sleep 5

echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'avn@list.ru', 'admin12345!')" | python /wapp/source/manage.py shell

echo "Django docker is fully configured successfully."

python /wapp/source/main.py