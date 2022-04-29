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
from project.serializers import TaskSerializerReadOnly, TaskSerializerWriteOnly, TeamSerializerReadOnly, TeamSerializerWriteOnly
from resource.models import Role
from resource.serializers import UserSerializerReadOnly, UserSerializerWriteOnly


# Create your views here.

User = get_user_model()

def get_resource_from_email(email):
    try:
        resource = User.objects.select_related('role').get(email=email)
    except:
        return False
    else:
        return resource
        

class TeamViewSet(ModelViewSet):
    queryset = User.objects.all()
    
    http_method_names= ['post']
    
    def get_serializer_class(self):
        
        if self.action in ['create', 'update', 'partial_update']:
            return TeamSerializerWriteOnly
        else:
            return TeamSerializerReadOnly
    
    def create(self, request, *args, **kwargs):
        print('printing request data')
        print(request.data)
        request_user_email = request.user.email
        request_user = User.objects.select_related('role').get(email=request_user_email)
        user_role = request_user.role.designation
        context = {}

        # Only 'user' can create a team 
        
        if user_role == 'user':
            data = request.data
            if 'team_members' not in data.keys():
                return Response({"error": "List of team member emails is required to create a team"})
            many = isinstance(data, list)
            team_lead_email = request.data.get('team_lead')
            team_lead = get_resource_from_email(team_lead_email)
            
            # Cannot make someone a team lead if their role is not of a team lead
            
            if team_lead and team_lead.role.designation == 'team_lead':
                context['team_member_emails'] = data.pop('team_members')
                data['team_lead'] = team_lead.id
                serializer = self.get_serializer_class()
                serializer = serializer(data=data, many=many, context=context)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                    headers=headers
                )
            else :
                return Response({
                    "error": "either resource does not exist or is not a team lead"},
                                status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({"error": "Only users can create a team"},
                            status = status.HTTP_400_BAD_REQUEST)
    
    
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
        
        # only 'user' can create a team 
        
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
        """ This method is only accessible by team leads"""
        
        permission_classes = (IsAuthenticated,)
        
        user_email = request.user.email
        user = User.objects.select_related('role').get(email = user_email)
        user_role = user.role.designation
        
        ## act accordingly with team lead and team member permissions
        
        if user_role == 'team_lead':
            task = Task.objects.get(id=kwargs.get('pk'))
            
            # team lead can only make changes if the task is assigned to his/ her team 
            
            if task.team.team_lead == user:
                state = request.data.get('status')
                try:
                    state = State.objects.get(status=state)
                except:
                    return Response({"error": "invalid status"}, status=status.HTTP_400_BAD_REQUEST)
                state = state.id
                request.data["status"] = state
                return super().update(request,*args, **kwargs)
            else:
                return Response({
                    "error": "You cannot update this task since it's not assigned to your team"
                    }, status=status.HTTP_400_BAD_REQUEST)
                
        else:
            return Response({
                "error": "Only team leads can update an entire task"
                }, status=status.HTTP_400_BAD_REQUEST)
        
        
    def partial_update(self, request, *args, **kwargs):
        """ This method will help team members update the status of the task"""
        
        serializer = self.get_serializer_class()
        user_email = request.user.email
        user = User.objects.select_related('role').get(email = user_email)
        user_role = user.role.designation
        if user_role == 'team_member':
            task = Task.objects.prefetch_related('team_members').get(id=kwargs.get('pk'))
            task_assigned = False
            associated_members = task.team_members.all()
            
            # Only team members that are assigned this task can make changes to the status
            
            for member in associated_members:
                if member.email == user.email:
                    task_assigned = True
            if task_assigned: 
        
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
                    status=status.HTTP_200_OK,
                    headers=headers
                )
            else:
                return Response({
                    "error": "you don't have permission to update this task"
                    }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Only assigned team members can update the status through patch"})

    