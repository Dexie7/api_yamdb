from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import (
    CreateUserViewSet,
    CategoryViewSet,
    CommentViewSet,
    CreateToken,
    GenreViewSet,
    MeAPIView,
    ReviewViewSet,
    TitleViewSet,
    UserViewSet
)

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register(
    prefix=r'(?P<version>v1)/categories',
    viewset=CategoryViewSet,
    basename='categories',
)
router_v1.register(
    prefix=r'(?P<version>v1)/genres',
    viewset=GenreViewSet,
    basename='genres',
)
router_v1.register(
    prefix=r'(?P<version>v1)/titles',
    viewset=TitleViewSet,
    basename='titles',
)
router_v1.register(
    prefix=r'(?P<version>v1)/titles/(?P<title_id>\d+)/reviews',
    viewset=ReviewViewSet,
    basename='reviews',
)
router_v1.register(
    prefix=(r'(?P<version>v1)/titles/(?P<title_id>\d+)/'
            r'reviews/(?P<reviews>\d+)/comments'),
    viewset=CommentViewSet,
    basename='comments',
)
router_v1.register(
    prefix=r'(?P<version>v1)/users',
    viewset=UserViewSet,
    basename='users',
)

router_v1.register(
    prefix=r'(?P<version>v1)/auth/signup',
    viewset=CreateUserViewSet,
    basename='auth/signup',)

token_auth_urls = [
    path(
        'auth/token/',
        CreateToken.as_view(),
        name='token_obtain_pair'
    )
]

urlpatterns = [
    re_path(
        r'(?P<version>v1)/users/me',
        MeAPIView.as_view(),
        name='users-me'
    ),
    path('', include(router_v1.urls)),
    path('v1/', include(token_auth_urls))
]
