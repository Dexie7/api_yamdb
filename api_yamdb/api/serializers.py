from rest_framework import serializers
from reviews.models import User


class CreateUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('email', 'username',)


class GetTokenSerializer(serializers.ModelSerializer):
    confirmation_code = serializers.SlugField(required=True)
    username = serializers.SlugField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code',)


class UsersSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    username = serializers.SlugField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role',)
