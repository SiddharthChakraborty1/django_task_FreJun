from functools import partial
from os import stat
from turtle import update
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from jsonschema import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from project.models import Task, Team, State
from project.serializers import TaskSerializer

# Create your views here.

User = get_user_model()


def check_user(email: str):
    """ Checks if user with the given email is present in the database or not """

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return False
    else:
        return user
    

@api_view(['POST'])
def create_team(request, *args, **kwargs):
    """ Creates a team, for team lead and members, email is required """
    
    permission_classes = (IsAuthenticated,)
    
    user_email = request.user.email
    user = User.objects.select_related('role').get(email = user_email)
    user_role = user.role.designation
    if user_role == 'user':
        data = request.data
        name = data.get('name')
        team_lead_email = data.get('team_lead').strip()
        team_member_emails = data.get('team_members') # This should be a list
        
        bad_request = True
        error_message = ''
        
        team_lead = check_user(team_lead_email)
        team = None
        if team_lead:
            team_lead.designation = 'team_lead'
            team_lead.save()
            try:
                
                team = Team.objects.create(name=name, team_lead=team_lead)
                
            except IntegrityError:
                
                bad_request = True
                error_message = 'Team with same name and team_lead is already present in the database'
                
            else:
                
                for member_email in team_member_emails:
                    team_member = check_user(member_email)
                    if team_member:
                        team_member.designation = 'team_member'
                        team_member.save()
                        team.team_members.add(team_member)
                        return Response({"Success":"Team Created Successfully!",
                                        "team": {
                                            "id": team.id,
                                            "name": team.name
                                        }}
                                        , status=status.HTTP_201_CREATED)
                    else:
                        bad_request = True
                        error_message = f'no user with email {member_email} present in database'
                        
        else:
            
            bad_request = True
            error_message = f'no team_lead with email {team_lead_email} present in database'
        
        if bad_request:
            
            return Response({"Error": error_message},
                            status=status.HTTP_400_BAD_REQUEST)
     
    else:
        return Response({"error": "Onlu users can create teams"})       
                
        
    
class TaskViewset(ModelViewSet):
    
    permission_classes = (IsAuthenticated,)
    
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    
    http_method_names = ['post', 'put', 'patch']
    
    
    def create(self, request, *args, **kwargs):
        data = request.data
        print(request.user.email)
        
        user_email = request.user.email
        user = User.objects.select_related('role').get(email=user_email)
        print(user.role)
        if user.role.designation == 'user':

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data,
                        status = status.HTTP_201_CREATED)
        else:
            return Response({"error": "Only users can create tasks!"})
        
    def update(self, request, *args, **kwargs):
        """ This method is only accessible by team leads and users"""
        
        permission_classes = (IsAuthenticated,)
        
        user_email = request.user.email
        user = User.objects.select_related('role').get(email = user_email)
        user_role = user.role.designation
        
        ## act accordingly with team lead and team member permissions
        
        if user_role in ['team_lead', 'user']:
            return super().update(request,*args, **kwargs)
                
        else:
            return Response({"error": "Only team leads or users can update tasks through put method"})
        
    def partial_update(self, request, *args, **kwargs):
        user_email = request.user.email
        user = User.objects.select_related('role').get(email = user_email)
        user_role = user.role.designation
        data = request.data
        status = data.get('status')
        task_id = kwargs.get('pk')
        try:
            status = State.objects.get(status = status)
        except State.DoesNotExist:
            return Response({"error": "Invalid status provided"})
        else:
            task = Task.objects.select_related('status', 'team').get(id=task_id)
            task.status = status
            task.save()
            return Response({
                "name": task.name,
                "description": task.description,
                "id": task.id,
                "status": task.status.status,
                "team": {
                    "name": task.team.name
                }
            })
    
    