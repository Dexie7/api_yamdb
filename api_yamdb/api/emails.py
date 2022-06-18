from django.core.mail import send_mail
from .tokens import create_confirmation_code


def send_email_confirmation(user):
    send_mail(
        'Код подтверждения регистрации',
        f"Ваш код для получения токена:"
        f"{create_confirmation_code(user)}",
        from_email=None,
        fail_silently=False,
        recipient_list=['romasan888888@gmail.com']
    )
