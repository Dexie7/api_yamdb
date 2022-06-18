from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import (CreateUserViewSet, AdminUserViewSet,
                    UsersViewSet, get_token, CurrentUserViewSet)

router_v1_auth = DefaultRouter()
router_v1_auth.register('signup', CreateUserViewSet, basename='signup')

router_v1_users = DefaultRouter()
router_v1_users.register('users', UsersViewSet, basename='users')
router_v1_users.register(r'users(\b(?!/me)\b)',
                         AdminUserViewSet,
                         basename='users-edit')
router_v1_users.register(
    'users/me', CurrentUserViewSet, basename='users-detail')

urlpatterns = [
    path('v1/', include(router_v1_users.urls)),
    path('v1/auth/', include(router_v1_auth.urls)),
    path('v1/auth/token/', get_token)
]
