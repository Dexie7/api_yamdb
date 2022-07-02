from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone


SIGNUP_ERROR_MESSAGE = 'Ошибка, имя me зарезервировано системой.'


def username_validator(value):
    if value == 'me':
        raise ValidationError(SIGNUP_ERROR_MESSAGE)

    RegexValidator(
        r'^[\w.@+-]+$',
        message="Может содержать только буквы, "
        "цифры либо символы: '@', '.', '+', '-', '_'",
        code='Некорректное имя позльзователя'
    )(value=value)


def year_validator(value):
    if value > timezone.now().year:
        raise ValidationError(
            (f'{value} год не должен быть больше нынешнего!'),
        )
