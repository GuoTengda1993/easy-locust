from locust.core import HttpLocust, Locust, TaskSet, TaskSequence, task, seq_task
from locust.exception import InterruptTaskSet, ResponseError, RescheduleTaskImmediately
from .util.locustFileFactory import make_locustfile
__version__ = "0.1.11"


def factory(data):
    return make_locustfile(data)
