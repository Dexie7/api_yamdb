from rest_framework import serializers

from reviews.models import (
    Category,
    Comment,
    Genre,
    Review,
    Title,
    User,
    ROLE_CHOICES
)


REVIEW_ERROR_MESSAGE = "Уже есть ревью на это произведение."
SIGNUP_ERROR_MESSAGE = 'Ошибка, имя me зарезервировано системой.'
USERNAME_REGEX = r'^[\w.@+-]+$'


class UserSerializer(serializers.ModelSerializer):
    """Сериалазер для модели User."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )


class RestrictedUserRoleSerializer(UserSerializer):
    """Сериалазер для модели User, ендпоинта users/me, роль user."""
    role = serializers.ChoiceField(ROLE_CHOICES, read_only=True)


class SignupSerializer(serializers.Serializer):
    """Сериалазер без модели, для полей username и email."""
    username = serializers.RegexField(
        regex=USERNAME_REGEX, max_length=150)
    email = serializers.EmailField()

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(SIGNUP_ERROR_MESSAGE)
        return value


class TokenSerializer(serializers.Serializer):
    """Сериалазер без модели, для полей username и confirmation_code."""
    username = serializers.RegexField(regex=USERNAME_REGEX, max_length=150,)
    confirmation_code = serializers.CharField(max_length=50, required=True)


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
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')


class ReviewSerializer(serializers.ModelSerializer):
    """Сериалазер для модели Review."""
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['title']

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
        fields = '__all__'
        read_only_fields = ['review']
