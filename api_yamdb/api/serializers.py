from rest_framework import serializers
from reviews.models import User, Category, Comment, Review, Genre, Title
from rest_framework.validators import UniqueTogetherValidator


class ReviewSerializer(serializers.ModelSerializer):

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review
        read_only_fields = ('author',)

    def validate_score(self, value):
        if not (0 < value <= 10):
            raise serializers.ValidationError('Поставьте оценку от 1 до 10!')
        return value

    def validate(self, data):
        if (
            (not data.get('text') and data.get('score'))
            or (data.get('text') and not data.get('score'))
            or (not data.get('text') and not data.get('score'))
        ):
            raise serializers.ValidationError(
                'Отсутствуют обязательные поля!')

        return data


class CommentSerializer(serializers.ModelSerializer):

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
        read_only_fields = ('author',)

    def validate(self, data):
        if not data.get('text'):
            raise serializers.ValidationError(
                'Отсутствует обязательное поле!')
        return data

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
