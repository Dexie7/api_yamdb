from django.contrib.auth.tokens import PasswordResetTokenGenerator

from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import User

generator = PasswordResetTokenGenerator()


def create_confirmation_code(user: User) -> str:
    """Создание confirmation_code для получения токена"""
    return generator.make_token(user)


def check_confirmation_code(user: User, code: str) -> bool:
    """Проверка на правильность confirmation_code."""
    valid_code = generator.make_token(user)
    return valid_code == code


def create_token_for_user(user: User) -> str:
    """Создание JWT токена"""
    refresh = RefreshToken.for_user(user)

    return {
        'token': str(refresh.access_token)
    }
