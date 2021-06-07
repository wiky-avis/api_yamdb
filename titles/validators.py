import datetime

from django.core.exceptions import ValidationError


def year_validator(year):
    current_year = datetime.date.today().year
    if year > current_year:
        raise ValidationError(
            'Год произведения не может быть больше текущего')
