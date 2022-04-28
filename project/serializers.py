
from unicodedata import name

from attr import fields
from jsonschema import ValidationError
from project.models import Task, Team, State
from rest_framework.serializers import ModelSerializer, ValidationError

from resource.models import Role
from resource.serializers import UserSerializer


def send_email(email_address):
    pass

class TeamSerializer(ModelSerializer):
    team_lead = UserSerializer(read_only=True)
    team_members = UserSerializer(read_only=True, many=True)
    
    class Meta:
        model = Team
        fields= ('name', 'team_lead', 'team_members')
        
class TaskSerializer(ModelSerializer):
    
    team = TeamSerializer(read_only=True)
    class Meta:
        model= Task
        fields = '__all__'
