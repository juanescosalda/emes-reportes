import numbers
from datetime import datetime

MONTHS = \
    {
        'ene.': '1',
        'feb.': '2',
        'mar.': '3',
        'abr.': '4',
        'may.': '5',
        'jun.': '6',
        'jul.': '7',
        'ago.': '8',
        'sep.': '9',
        'oct.': '10',
        'nov.': '11',
        'dic.': '12'
    }


def is_int(value) -> bool:
    return isinstance(value, numbers.Integral)


def is_num(value) -> bool:
    return isinstance(value, numbers.Number)


def is_nan(value: str) -> bool:
    return value == 'nan'


def clean_currency(value):
    """ 
    Remove $ and , symbols from string-currency format
    """
    if isinstance(value, str):
        return value.replace('$', '').replace(',', '')

    return value


def format_datetime(s: str) -> datetime:
    d = s.split(' ')[0].split('-')
    return datetime.strptime(
        f'{d[0]}/{MONTHS[d[1]]}/{d[2]}',
        '%d/%m/%Y'
    )
