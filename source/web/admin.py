from django.contrib import admin
from . models import ActiveUsers
from . models import Programs

admin.site.register(ActiveUsers)
admin.site.register(Programs)