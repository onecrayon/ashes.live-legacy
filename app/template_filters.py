from datetime import date

from app import app


@app.template_filter('copyright')
def copyright(value):
    return '{}-{}'.format(value, date.today().year)
