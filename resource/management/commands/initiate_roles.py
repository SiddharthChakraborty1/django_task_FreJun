from distutils import core
import email
from django.core.management.base import BaseCommand, CommandParser, CommandError
from django.contrib.auth import get_user_model

from resource.models import Role


class Command(BaseCommand):
    """ Custom management command to create roles in database """

    def handle(self, *args, **kwargs):
        help = ' Creates roles in the db that will be used by the app '
        
        roles = Role.objects.all()
        if len(roles)>0:
            raise CommandError("Roles already present in the database")
        roles = Role.ROLES
        for role in roles:
            Role.objects.create(designation = role)
            
        self.stdout.write(self.style.SUCCESS("Roles Created"))
