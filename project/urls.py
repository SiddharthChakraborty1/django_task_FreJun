from django.urls import path, include

from project.views import create_team

urlpatterns = [
    path('create_team/', create_team, name='create_team_url')
]
