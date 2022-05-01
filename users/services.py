import random
import string
from smtplib import SMTPException
from typing import Dict

from django.conf.global_settings import EMAIL_HOST_USER
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


def generate_code() -> str:
    """Генерирует случайны код из букв, цифр.
    Через цикл получаем строку, с кодом.
    """
    alphabet = string.digits + string.ascii_uppercase + string.ascii_letters
    code_to = str()
    for i in random.sample(alphabet, 6):
        code_to += i
    return code_to


def get_confirmation_code(username: str) -> str:
    """Получает токен определенного юзера
     и сохраняет его в confirmation_code.
     """
    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist as e:
        raise e
    confirmation_code = generate_code()
    user.confirmation_code = confirmation_code
    user.is_active = False
    user.save()
    return confirmation_code


def send_code_to_email(username: str, email: str) -> None:
    """Отправляет сообщение с кодом по переданному адресу."""
    confirmation_code = get_confirmation_code(username)
    try:
        email = EmailMessage(
            body=f'{username} ваш код {confirmation_code}',
            from_email=EMAIL_HOST_USER,
            to=[f'{email}'],
        )
        email.send()
    except SMTPException as e:
        raise e


def get_tokens_for_user(user: str) -> Dict[str, str]:
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
