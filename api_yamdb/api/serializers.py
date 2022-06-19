from rest_framework import serializers
from reviews.models import User
from rest_framework.validators import UniqueTogetherValidator


class CreateUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('email', 'username',)

    def validate(self, data):
        username = data['username']
        email = data['email']
        if username == 'me':
            raise serializers.ValidationError(
                "Использовать имя 'me' в качестве username запрещено.")
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                "Пользователь с такой почтой уже существует.")
        return data

    validators = [
        UniqueTogetherValidator(
            queryset=User.objects.all(),
            fields=('username', 'email')
        )
    ]


class GetTokenSerializer(serializers.ModelSerializer):
    confirmation_code = serializers.SlugField(required=True)
    username = serializers.SlugField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code',)


class UsersSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role',)

    def validate(self, data):
        username = data['username']
        email = data['email']
        if username == 'me':
            raise serializers.ValidationError(
                "Использовать имя 'me' в качестве username запрещено.")
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                "Email` должен быть уникальный у каждого прользователя.")
        return data

    validators = [
        UniqueTogetherValidator(
            queryset=User.objects.all(),
            fields=('username', 'email')
        )
    ]


class AdminPatchUsersSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)
    username = serializers.SlugField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role',)

    def validate(self, data):
        if ('role' in data
                and data['role'] not in ['user', 'moderator', 'admin']):
            raise serializers.ValidationError(
                "Нельзя назначать произвольные роли пользователям.")
        return data


class EditUsersSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)
    username = serializers.SlugField(required=False)
    role = serializers.StringRelatedField()

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role',)
