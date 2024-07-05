from django.core.exceptions import ValidationError


def validate_name(value):
    if value == "me":
        return ValidationError("Не корректное имя пользователя")
    else:
        return value
