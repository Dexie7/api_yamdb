from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CreateUserViewSet, AdminUserViewSet, CurrentUserView,
                    UsersViewSet, get_token, CommentViewSet, ReviewViewSet)


router_v1 = DefaultRouter()
router_v1.register(
    r'^titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
)
router_v1.register(
    r'^titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments',
)

router_v1_auth = DefaultRouter()
router_v1_auth.register('signup', CreateUserViewSet, basename='signup')

router_v1_users = DefaultRouter()
router_v1_users.register('users', UsersViewSet, basename='users')
router_v1_users.register(r'users(\b(?!/me)\b)',
                         AdminUserViewSet,
                         basename='users-edit')


urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/', include(router_v1_users.urls)),
    path('v1/auth/', include(router_v1_auth.urls)),
    path('v1/auth/token/', get_token),
    path('v1/users/me/', CurrentUserView.as_view())
]
