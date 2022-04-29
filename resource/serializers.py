from attr import fields
from rest_framework.serializers import ModelSerializer, ValidationError
from project.models import Team
from resource.models import Role, User


class RoleSerializer(ModelSerializer):
    
    class Meta:
        
        model = Role
        fields = ['designation']
        
        
class UserSerializerReadOnly(ModelSerializer):
    role = RoleSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ('email', 'name', 'role')
        
class UserSerializerWriteOnly(ModelSerializer):
    
    class Meta:
        model = User
        fields = ('email', 'name', 'role')
        
    
            
            
            