
from unicodedata import name

from attr import fields
from psycopg2 import IntegrityError
from project.models import Task, Team, State
from rest_framework.serializers import ModelSerializer, ValidationError

from resource.models import Role, User
from resource.serializers import UserSerializerReadOnly
from project.tasks import send_email_to_team_lead_task

class StatusSerializer(ModelSerializer):
    
    class Meta:
        model = State
        fields = 'status'
        
class TeamSerializerReadOnly(ModelSerializer):
    team_lead = UserSerializerReadOnly(read_only=True)
    #team_members = UserSerializerReadOnly(read_only=True, many=True)
    
    class Meta:
        model = Team
        fields= ('name', 'team_lead')
        
class TeamSerializerWriteOnly(ModelSerializer):
    
    class Meta:
        model = Team
        fields = '__all__'
    
    def create(self, validated_data):
        print('printing validated data')
        print(validated_data)
        print(self.context)
        name = validated_data.get('name')
        team_lead = validated_data.get('team_lead')
        team = Team.objects.create(name=name, team_lead=team_lead)
        team_member_emails = self.context.get('team_member_emails')
        try:
            for member_email in team_member_emails:
                team_member = User.objects.get(email=member_email)
                print('printing team member')
                print(team_member)
                team.team_members.add(team_member)
        except:
            raise ValidationError(
                {"error": "Something went wrong while adding team members"})

        return team
        
class TaskSerializerReadOnly(ModelSerializer):
    
    status = StatusSerializer
    team = TeamSerializerReadOnly(read_only=True)
    team_members = UserSerializerReadOnly(many=True)
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
                
                # send email with the task description to the team lead
                
                send_email_to_team_lead_task.delay(
                    task.team.team_lead.name,
                    task.team.team_lead.email,
                    task.description
                )
        except Task.MultipleObjectsReturned:
            raise ValidationError({"error": "Multiple similar tasks already exist"})
        else:
            return task