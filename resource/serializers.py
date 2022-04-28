from attr import fields
from rest_framework.serializers import ModelSerializer
from resource.models import Role, User


class RoleSerializer(ModelSerializer):
    
    class Meta:
        
        model = Role
        fields = ['designation']
        
        
class UserSerializer(ModelSerializer):
    role = RoleSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ('email', 'name', 'role')