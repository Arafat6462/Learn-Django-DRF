from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta): # we can avoid inheriting Meta class but to keep the code consistent we are inheriting it and overriding only the fields attribute that we want to change
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name',]