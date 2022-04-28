from distutils import core
import email
from django.core.management.base import BaseCommand, CommandParser
from django.contrib.auth import get_user_model

from resource.models import Role

class Command(BaseCommand):
    """ Custom management command to create a user with specific roles """
    
    def add_arguments(self, parser: CommandParser):
        parser.add_argument('-r','--role', type=str, help="Specify the role of that particular user")
        parser.add_argument('-n', '--name', type=str, help="Specify user's name")
        parser.add_argument('-e', '--email', type=str, help="Specify the role of that particular user")
        parser.add_argument('-p', '--password', type=str, help="Specify user's password")
        
    def handle(self, *args, **kwargs):
        help = ' Creates User from the command line '
        
        if 'role' and 'name' and 'email' and 'password' in kwargs.keys():
            role = kwargs.get('role').strip()
            name = kwargs.get('name').strip()
            email = kwargs.get('email').strip()
            password = kwargs.get('password').strip()
            
            if role in Role.ROLES:
                role = Role.objects.get(designation=role)
                User = get_user_model()
                user = User.objects.create(email=email, name=name, role=role)
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS("User Created"))
            else:
                self.stdout.write(self.style.ERROR("Invalid Role"))
        else:
            self.stdout.write(self.style.ERROR("INVALID ARGUMENTS"))
                
                
        