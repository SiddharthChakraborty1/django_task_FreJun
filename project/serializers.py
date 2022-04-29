
from unicodedata import name

from attr import fields
from psycopg2 import IntegrityError
from project.models import Task, Team, State
from rest_framework.serializers import ModelSerializer, ValidationError

from resource.models import Role
from resource.serializers import UserSerializer
from project.tasks import send_email_to_team_lead_task


def send_email(email_address):
    pass

class TeamSerializer(ModelSerializer):
    team_lead = UserSerializer(read_only=True)
    team_members = UserSerializer(read_only=True, many=True)
    
    class Meta:
        model = Team
        fields= ('name', 'team_lead', 'team_members')
        
class TaskSerializerReadOnly(ModelSerializer):
    
    team = TeamSerializer(read_only=True)
    class Meta:
        model= Task
        fields = '__all__'

class TaskSerializerWriteOnly(ModelSerializer):
    
    class Meta:
        model = Task
        fields = '__all__'
        
        
    def create(self, validated_data):
        
        try:
            task, created = Task.objects.get_or_create(**validated_data)
            if created:
                send_email_to_team_lead_task.delay(
                    task.team.team_lead.name,
                    task.team.team_lead.email,
                    task.description
                )
        except Task.MultipleObjectsReturned:
            raise ValidationError({"error": "Multiple similar tasks already exist"})
        else:
            return task