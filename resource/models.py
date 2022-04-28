from email.policy import default
from random import choices
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin


# Create your models here.
class UserManager(BaseUserManager):

    def create_user(self, email, password, role='user'):
        """ Creates and returns a new user """
        user = None
        if not email or email in ['', ' ']:
            raise ValueError("Cannot create user without an email")
        if role in Role.ROLES:
            role = Role.objects.get(designation=role)
            user = self.model(email=self.normalize_email(email), role = role)
            user.set_password(password)
            user.save()
        else:
            raise ValueError("Invalid Role")

        return user

    def create_superuser(self, email, password):
        """ Creates and returns a new superuser """

        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save()

        return user


class Role(models.Model):
    """ Will be used to store the 3 roles team_lead, team_member and user """
    
    ROLES = ('team_lead', 'team_member', 'user')
    
    designation =           models.CharField(max_length=250, unique=True)
    
    def __str__(self) -> str:
        return self.designation
    

class User(AbstractBaseUser, PermissionsMixin):
    
    email =             models.EmailField(max_length=255, null=False, unique=True)
    name =              models.CharField(max_length=60)
    is_active =         models.BooleanField(default=True)
    is_staff =          models.BooleanField(default=False)
    role =              models.ForeignKey(Role, on_delete=models.CASCADE)

    USERNAME_FIELD = 'email'
    objects = UserManager()

    def __str__(self):
        return f'{self.name}~{self.email}'
