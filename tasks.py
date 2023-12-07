from celery_app import celery
from typing import Union


@celery.task
def do_operation(
    x: Union[int, float], y: Union[int, float], operator: str
) -> Union[int, float]:
    if operator == "+":
        return x + y
    elif operator == "-":
        return x - y
    elif operator == "*":
        return x * y
    elif operator == "/":
        if y == 0:
            raise ValueError("Деление на ноль")
        return x / y
    else:
        raise ValueError("Введите корректный оператор")
