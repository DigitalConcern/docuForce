from django.db import models


# Зарегситрировавшиеся пользователи добавляются в базу данных
class ActiveUsers(models.Model):
    user_id = models.BigIntegerField(primary_key=True)
    user_org_id = models.UUIDField(null=True)
    login = models.TextField()
    password = models.TextField()
    organization = models.UUIDField(null=True)
    refresh_token = models.TextField()
    access_token = models.TextField()
    current_document_id = models.TextField(null=True)
    tasks_amount = models.IntegerField(default=0)
    conversations_amount = models.IntegerField(default=0)
    eight_hour_notification = models.BooleanField(default=False)
    instant_notification = models.BooleanField(default=True)
    not_notification = models.BooleanField(default=False)
    new_tasks = models.IntegerField(default=0)
    new_convs = models.IntegerField(default=0)

    class Meta:
        db_table = "users"


class Stats(models.Model):
    users = models.IntegerField(default=0)
    documents = models.IntegerField(default=0)
    command_tasks = models.IntegerField(default=0)
    command_documents = models.IntegerField(default=0)
    command_search = models.IntegerField(default=0)
    command_messages = models.IntegerField(default=0)
    tasks_done = models.IntegerField(default=0)
    messages_done = models.IntegerField(default=0)

    class Meta:
        db_table = "stats"
