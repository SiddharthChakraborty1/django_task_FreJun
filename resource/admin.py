from django.contrib import admin
from resource.models import Role, User

# Register your models here.

@admin.register(User)
class AdminUser(admin.ModelAdmin):
    pass


