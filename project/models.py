from django.db import models
from resource.models import User

# Create your models here.

class State(models.Model):
    
    STATUS_List = ('assigned', 'in_progress', 'under_review', 'done')
    
    status = models.CharField(max_length=250, unique=True)
    

class Team(models.Model):
    
    name =              models.CharField(max_length=250)
    team_lead =         models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_lead')
    team_members =      models.ManyToManyField(User, related_name='team_members')
    
    class Meta:
        unique_together = ('name', 'team_lead')
        
    def __str__(self):
        return self.name
    
class Task(models.Model):
    
    name =              models.CharField(max_length=250)
    team =              models.ForeignKey(Team, null = True, on_delete=models.SET_NULL)
    status =            models.ForeignKey(State, default='assigned', null=True, on_delete=models.SET_NULL)
    description =       models.TextField()
    started_at =        models.DateTimeField(null=True)
    completed_at =      models.DateTimeField(null=True)
    
    def __str__(self) -> str:
        return self.name
    
    
