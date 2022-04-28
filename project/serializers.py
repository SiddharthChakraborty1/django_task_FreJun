
from unicodedata import name

from attr import fields
from jsonschema import ValidationError
from project.models import Task, Team, State
from rest_framework.serializers import ModelSerializer, ValidationError

from resource.models import Role


def send_email(email_address):
    pass

class TeamSerializer(ModelSerializer):
    
    class Meta:
        model = Team
        fields= '__all__'
        
class TaskSerializer(ModelSerializer):
    
    class Meta:
        model= Task
        fields = '__all__'
        
    def create(self, validated_data):
        task_name = validated_data.get('name'),
        task_description = validated_data.get('description')
        team = validated_data.get('team')
        try:
            task, created = Task.objects.get_or_create(name=task_name, description=task_description, team=team)
        except Task.MultipleObjectsReturned:
            raise ValidationError("A task with same name and team already exists")
        except:
            raise ValidationError("error occured try again")
        else:
            send_email(task.team.team_lead.email)
            return task
        