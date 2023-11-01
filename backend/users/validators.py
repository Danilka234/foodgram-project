import re

from django.forms import ValidationError


def validate_username_own(value):
    """Проверка вводимых данных пользователя при регистрации."""
    if value.lower() == "me":
        raise ValidationError("'me' не допустимое имя пользователя.")
    if re.match(r"^[a-zA-Z][a-zA-Z0-9-_\.]{1,20}$", value) is None:
        raise ValidationError("Недопустимый символ! Можно использовать: "
                              "`.`, `+` и `-`.")
    return value
