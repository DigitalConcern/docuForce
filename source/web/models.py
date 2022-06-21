from django.db import models


# Зарегситрировавшиеся пользователи добавляются в базу данных
class ActiveUsers(models.Model):
    user_id = models.IntegerField(primary_key=True)
    password = models.TextField(null=True)
    is_admin = models.BooleanField()
    code_name = models.TextField()
    user_name = models.TextField()
    grade = models.TextField()
    link = models.TextField(null=True)
