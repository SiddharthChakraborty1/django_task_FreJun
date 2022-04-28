from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from project.models import Team

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
                    return Response({"Success":"Team Created Successfully!"}
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
        
                
        
    
   