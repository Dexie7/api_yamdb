from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.db.models import Avg

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (generics, mixins, permissions, status, views,
                            viewsets)
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.versioning import URLPathVersioning
from rest_framework_simplejwt.tokens import AccessToken


from reviews.models import Category, Genre, Review, Title, User

from .filter import TitlesFilter
from .permissions import (
    IsAdmin,
    IsAdminOrReadOnly,
    ReadOnlyOrIsAdminOrModeratorOrAuthor,
)
from .serializers import (
    CategorySerializer, CommentSerializer,
    GenreSerializer, ReviewSerializer, SignupSerializer,
    TitleCreate, TitleSerializer, TokenSerializer,
    RestrictedUserRoleSerializer, UserSerializer
)
from api_yamdb.settings import FROM_EMAIL


class FirstVersioning(URLPathVersioning):
    """Определяет версию api в urls, и во viesets."""
    default_version = 'v1'
    allowed_versions = 'v1'


class APISignup(views.APIView):
    """View для регистрации и создания пользователя
    с последующей отсылкой confirmation code на email этого пользователя."""

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        email = serializer.validated_data['email']

        username_exists = User.objects.filter(username=username).exists()
        email_exists = User.objects.filter(email=email).exists()

        if not username_exists and not email_exists:
            user = User.objects.create(username=username, email=email)
        else:
            if not username_exists:
                return Response(
                    "Ошибка, email занят, просьба выбрать другой email.",
                    status=status.HTTP_400_BAD_REQUEST
                )
            user = get_object_or_404(User, username=username)
            if user.email != email:
                return Response(
                    "Ошибка, у пользователя другой email.",
                    status=status.HTTP_400_BAD_REQUEST
                )
        token = default_token_generator.make_token(user)
        send_mail(
            subject='Ваш код для получения api-токена.',
            message=f'Код: {token}',
            from_email=FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateToken(views.APIView):
    """Создание токена."""
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        confirmation_code = serializer.validated_data['confirmation_code']
        username = serializer.validated_data['username']
        user = get_object_or_404(User, username=username)
        if default_token_generator.check_token(
            user,
            confirmation_code
        ):
            token = AccessToken.for_user(user)
            return Response(
                {"token": f"{token}"},
                status=status.HTTP_200_OK
            )
        return Response(
            "Confirm code invalid",
            status=status.HTTP_400_BAD_REQUEST
        )


class UserViewSet(viewsets.ModelViewSet):
    """Viewset для модели  User."""
    versioning_class = FirstVersioning
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('username',)
    lookup_field = ('username')


class MeAPIView(generics.RetrieveUpdateAPIView):
    """Viewset для модели  User, ендпойнт users/me"""
    versioning_class = FirstVersioning
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = RestrictedUserRoleSerializer

    def get_object(self):
        return self.request.user


class TitleViewSet(viewsets.ModelViewSet):
    """Viewset для модели  Title."""
    versioning_class = FirstVersioning
    queryset = Title.objects.all().annotate(
        rating=Avg("reviews__score")).order_by('category')
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitlesFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleSerializer
        return TitleCreate


class BaseCategoryGenreView(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Базовый Viewset для моделей Category и Genre."""
    queryset = None
    serializer_class = None

    versioning_class = FirstVersioning
    permission_classes = (IsAdminOrReadOnly,)
    search_fields = ('name',)
    filter_backends = (SearchFilter,)
    lookup_field = ('slug')


class CategoryViewSet(BaseCategoryGenreView):
    """Viewset для модели  Category."""
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer


class GenreViewSet(BaseCategoryGenreView):
    """Viewset для модели  Genre."""
    queryset = Genre.objects.all().order_by('name')
    serializer_class = GenreSerializer


class BaseReviewCommentView(viewsets.ModelViewSet):
    """Базовый класс ревью и комментариев."""
    queryset = None
    serializer_class = None

    versioning_class = FirstVersioning
    permission_classes = (ReadOnlyOrIsAdminOrModeratorOrAuthor,)


class ReviewViewSet(BaseReviewCommentView):
    """Viewset для модели  Review."""
    serializer_class = ReviewSerializer

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get("title_id"))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(BaseReviewCommentView):
    """Viewset для модели  Comment."""
    versioning_class = FirstVersioning
    serializer_class = CommentSerializer

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get("reviews"))

    def get_queryset(self):
        return self.get_review().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
