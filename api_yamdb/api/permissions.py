from rest_framework import permissions

class ReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):

        return (
            request.method in permissions.SAFE_METHODS
        )

class AuthorOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
      
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

class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin()
            or request.method in permissions.SAFE_METHODS
        )

class ReadOnlyOrIsAdminOrModeratorOrAuthor(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            or request.method in permissions.SAFE_METHODS
        )

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return (
                request.user.is_moderator()
                or request.user.is_admin()
                or request.user == obj.author
            )
        return request.method in permissions.SAFE_METHODS