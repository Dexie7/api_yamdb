from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework import viewsets, mixins, permissions, status, views
from rest_framework.decorators import api_view, permission_classes

from .mixins import (
    ListCreateViewSet
)

from .serializers import (
    CreateUserSerializer,
    GetTokenSerializer,
    UsersSerializer,
    EditUsersSerializer,
    AdminPatchUsersSerializer
)
from reviews.models import User
from .emails import send_email_confirmation
from .tokens import check_confirmation_code, create_token_for_user
from .permissions import IsAdminUserCustom


class CreateUserViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer

    def create(self, request, *args, **kwargs):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_200_OK,
                        headers=headers)

    def perform_create(self, serializer):
        instance = serializer.save()
        send_email_confirmation(user=instance)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def get_token(request):
    serializer = GetTokenSerializer(data=request.data)
    if serializer.is_valid():
        user = get_object_or_404(User, username=request.data['username'])
        if check_confirmation_code(user, request.data['confirmation_code']):
            return Response(create_token_for_user(user),
                            status=status.HTTP_200_OK)
        return Response('Не верный код подтверждения',
                        status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersViewSet(ListCreateViewSet):
    permission_classes = [IsAdminUserCustom]
    queryset = User.objects.all()
    serializer_class = UsersSerializer


class AdminUserViewSet(viewsets.ViewSet):
    def get_permissions(self):
        permission_classes = [IsAdminUserCustom]
        return[permission() for permission in permission_classes]

    def retrieve(self, request, pk=None):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, username=pk)
        serializer = EditUsersSerializer(user)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, username=pk)
        serializer = AdminPatchUsersSerializer(data=request.data)
        serializer_user = AdminPatchUsersSerializer(
            user, data=request.data, partial=True)
        if serializer.is_valid() and serializer_user.is_valid():
            serializer_user.save()
            return Response(serializer_user.data,
                            status=status.HTTP_200_OK)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, username=pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CurrentUserView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        serialiser = UsersSerializer(instance=request.user)
        return Response(serialiser.data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None, format=None):
        serializer = EditUsersSerializer(data=request.data)
        serializer_user = EditUsersSerializer(
            request.user, data=request.data, partial=True)
        if serializer_user.is_valid() and serializer.is_valid():
            serializer_user.save()
            return Response(serializer_user.data,
                            status=status.HTTP_200_OK)
        return Response(serializer_user.errors,
                        status=status.HTTP_400_BAD_REQUEST)
