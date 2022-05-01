import json

from django_celery_beat.models import PeriodicTask, IntervalSchedule

from config.celery import app
from .services import save_state
from .models import Product





@app.task
def get_state_task(code, code_id):
    data = save_state(code, code_id)
    return data
