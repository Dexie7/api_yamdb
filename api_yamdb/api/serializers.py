from rest_framework import serializers

from api_yamdb.settings import (
    EMAIL_LENGTH,
    USERNAME_LENGTH,
    CONFIRMATION_CODE_LENGTH)
from reviews.models import (
    Category,
    Comment,
    Genre,
    Review,
    Title,
    User
)
from reviews.validators import (
    username_validator, email_validator, username_validator_regex)


REVIEW_ERROR_MESSAGE = "Уже есть ревью на это произведение."


class UserSerializer(serializers.ModelSerializer):
    """Сериалазер для модели User."""
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )

    def validate_username(self, value):
        username_validator(value)
        username_validator_regex(value=value)
        return value

    def validate_email(self, value):
        email_validator(value)
        return value


class RestrictedUserRoleSerializer(UserSerializer):
    """Сериалазер для модели User, ендпоинта users/me, роль user."""
    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


class SignupSerializer(UserSerializer):
    """Сериалазер без модели, для полей username и email."""
    email = serializers.EmailField(max_length=EMAIL_LENGTH)
    username = serializers.CharField(max_length=USERNAME_LENGTH)

    class Meta(UserSerializer.Meta):
        fields = ('email', 'username',)

    def validate_email(self, value):
        return value


class TokenSerializer(UserSerializer):
    """Сериалазер без модели, для полей username и confirmation_code."""
    username = serializers.CharField(max_length=USERNAME_LENGTH,)
    confirmation_code = serializers.CharField(
        max_length=CONFIRMATION_CODE_LENGTH, required=True)

    class Meta(UserSerializer.Meta):
        fields = ('username', 'confirmation_code',)


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
