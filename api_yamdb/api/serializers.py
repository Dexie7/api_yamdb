from django.conf import settings

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from reviews.models import (
    Category,
    Comment,
    Genre,
    Review,
    Title,
    User
)


REVIEW_ERROR_MESSAGE = "Уже есть ревью на это произведение."
SIGNUP_ERROR_MESSAGE = 'Ошибка, имя me зарезервировано системой.'
USERNAME_REGEX = r'^(?!me+$)[\w.@+-]+$'


class UserSerializer(serializers.ModelSerializer):
    """Сериалазер для модели User."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(SIGNUP_ERROR_MESSAGE)
        return value


class RestrictedUserRoleSerializer(UserSerializer):
    """Сериалазер для модели User, ендпоинта users/me, роль user."""
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )
        read_only_fields = ('role',)


class SignupSerializer(serializers.ModelSerializer):
    """Сериалазер без модели, для полей username и email."""
    email = serializers.EmailField(max_length=settings.EMAIL_LENGTH,)

    class Meta:
        model = User
        fields = ('email', 'username',)

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(SIGNUP_ERROR_MESSAGE)
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Пользователь с такой почтой уже существует.")
        return value

    validators = [
        UniqueTogetherValidator(
            queryset=User.objects.all(),
            fields=('username', 'email')
        )
    ]


class TokenSerializer(serializers.Serializer):
    """Сериалазер без модели, для полей username и confirmation_code."""
    username = serializers.RegexField(
        regex=USERNAME_REGEX, max_length=settings.USERNAME_LENGTH,)
    confirmation_code = serializers.CharField(
        max_length=settings.CONFIRMATION_CODE_LENGTH, required=True)

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(SIGNUP_ERROR_MESSAGE)
        return value


class GenreSerializer(serializers.ModelSerializer):
    """Сериалазер для модели Genre."""
    class Meta:
        fields = ('name', 'slug')
        model = Genre


class CategorySerializer(serializers.ModelSerializer):
    """Сериалазер для модели Category."""
    class Meta:
        fields = ('name', 'slug')
        model = Category


class TitleSerializer(serializers.ModelSerializer):
    """Сериалазер для модели Title."""
    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category')
        read_only_fields = fields


class TitleCreate(serializers.ModelSerializer):
    """Сериалазер для модели Title."""
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
    )

    class Meta:
        model = Title
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    """Сериалазер для модели Review."""
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        if self.context['view'].action != 'create':
            return data
        if Review.objects.filter(
            title=self.context['view'].kwargs.get('title_id'),
            author=self.context['request'].user
        ).exists():
            raise serializers.ValidationError(REVIEW_ERROR_MESSAGE)
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериалазер для модели Comment."""
    author = serializers.SlugRelatedField(read_only=True,
                                          slug_field='username',)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
