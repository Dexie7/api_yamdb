from rest_framework import serializers
from reviews.models import Comment, Review


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
