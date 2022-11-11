import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    today = datetime.date.today().year
    return {"year": today}
