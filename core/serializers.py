from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta): # we can avoid inheriting Meta class but to keep the code consistent we are inheriting it and overriding only the fields attribute that we want to change
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name',]


# Custom serializer for representing user data
class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ['id', 'username', 'email', 'first_name', 'last_name',]