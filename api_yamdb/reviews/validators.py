from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from reviews import models


SIGNUP_ERROR_MESSAGE = 'Ошибка, имя me зарезервировано системой.'


def username_validator(value):
    if value == 'me':
        raise ValidationError(SIGNUP_ERROR_MESSAGE)


def username_validator_regex(value):
    validator = RegexValidator(
        r'^[\w.@+-]+$',
        message='Может содержать только буквы, '
        'цифры либо символы @ /. / + / - / _',
        code='Некорректное имя позльзователя'
    )
    return validator(value=value)


def email_validator(value):
    if models.User.objects.filter(email=value).exists():
        raise ValidationError("Пользователь с такой почтой уже существует.")
