from ftplib import error_temp
from functools import partial
from os import stat
from telnetlib import STATUS
from turtle import update
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from jsonschema import ValidationError
from requests import post
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from project.models import Task, Team, State
from project.serializers import TaskSerializerReadOnly, TaskSerializerWriteOnly


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
        return Response({"error": "Only users can create teams"})       
                
        
    
class TaskViewset(ModelViewSet):
    
    permission_classes = (IsAuthenticated,)
    
    queryset = Task.objects.all()
    serializer_class = TaskSerializerReadOnly
    
    def get_serializer_class(self):
        print('printing action')
        print(self.action)
        if self.action in ['create', 'update', 'partial_update']:
            print('write_only')
            return TaskSerializerWriteOnly
        else:
            print('read_only')
            return TaskSerializerReadOnly
    
    def create(self, request, *args, **kwargs):
        data = request.data
        many = isinstance(data,list)
        request_user_email = request.user.email
        request_user = User.objects.select_related('role').get(email=request_user_email)
        user_role = request_user.role.designation
        if user_role == 'user':
            data = request.data
            serializer = self.get_serializer_class()
            state = data.get('status')
            try:
                state = State.objects.get(status=state)
            except:
                return Response({"error": "invalid status"}, status=status.HTTP_400_BAD_REQUEST)
            data['status'] = state.id
            serializer = serializer(data=data, many=many)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            print('printing serializer data')
            print(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        else:
            return Response({
                "error": "Only users can create a task"
            }, status=status.HTTP_400_BAD_REQUEST)
            
                
        
    def update(self, request, *args, **kwargs):
        """ This method is only accessible by team leads and users"""
        
        permission_classes = (IsAuthenticated,)
        
        user_email = request.user.email
        user = User.objects.select_related('role').get(email = user_email)
        user_role = user.role.designation
        
        ## act accordingly with team lead and team member permissions
        
        if user_role in ['team_lead', 'user']:
            state = request.data.get('status')
            try:
                state = State.objects.get(status=state)
            except:
                return Response({"error": "invalid status"}, status=status.HTTP_400_BAD_REQUEST)
            state = state.id
            request.data["status"] = state
            return super().update(request,*args, **kwargs)
                
        else:
            return Response({"error": "Only team leads or users can update tasks through put method"})
        
    def partial_update(self, request, *args, **kwargs):
        
        
        serializer = self.get_serializer_class()
        user_email = request.user.email
        user = User.objects.select_related('role').get(email = user_email)
        user_role = user.role.designation
        data = request.data
        instance = self.get_object()
        state = data.get('status')
        try:
            state = State.objects.get(status=state)
        except:
             return Response({"error": "invalid status"}, status=status.HTTP_400_BAD_REQUEST)
        state = state.id
        data = {"status": state}
        serializer = serializer(data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    

        
    
    