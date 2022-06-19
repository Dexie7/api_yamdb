from rest_framework import permissions


class IsAdminUserCustom(permissions.BasePermission):
    message = "У вас недостаточно прав для выполнения данного действия!"

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return (request.user.role == 'admin'
                    or request.user.is_superuser)


class IsModeratorUserCustom(permissions.BasePermission):
    message = "У вас недостаточно прав для выполнения данного действия!"

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.role == 'moderator'
