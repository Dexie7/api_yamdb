from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework import viewsets, mixins, permissions, status
from rest_framework.decorators import api_view, permission_classes

from .mixins import (
    ListCreateViewSet
)

from .serializers import (
    CreateUserSerializer,
    GetTokenSerializer,
    UsersSerializer
)
from reviews.models import User
from .emails import send_email_confirmation
from .tokens import check_confirmation_code, create_token_for_user


class CreateUserViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        return send_email_confirmation(user=instance)


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
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UsersSerializer


class AdminUserViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAdminUser]

    def retrieve(self, request, pk=None):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, username=pk)
        serializer = UsersSerializer(user)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, username=pk)
        serializer = UsersSerializer(data=request.data)
        serializer_user = UsersSerializer(
            user, data=request.data, partial=True)
        if serializer.is_valid() and serializer_user.is_valid():
            serializer_user.save()
            return Response(serializer_user.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, username=pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CurrentUserViewSet(viewsets.ViewSet):
    def list(self, request):
        serialiser = UsersSerializer(instance=request.user)
        return Response(serialiser.data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        serializer = UsersSerializer(data=request.data)
        serializer_user = UsersSerializer(
            instanse=request.user, data=request.data, partial=True)
        if serializer_user.is_valid() and serializer.is_valid():
            serializer_user.save()
            return Response(serializer_user.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer_user.errors,
                        status=status.HTTP_400_BAD_REQUEST)
