from django.core.exceptions import ValidationError


def validate_name(value):
    if value == "me":
        raise ValidationError("Не корректное имя пользователя")
    return value
