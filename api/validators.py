import datetime

from django.core.exceptions import ValidationError


def year_validator(value):
    if value > datetime.datetime.now().year:
        raise ValidationError(
            message="Год не должен быть больше текущего!",
            params={'value': value},
        )
