# -*- coding: utf-8 -*-
from locust.wait_time import between
from locust import TaskSet, task
from locust.contrib.fasthttp import FastHttpLocust


class PressureTest(TaskSet):

    @task(100)
    def test1(self):
        self.client.get('/')


class ApiTest(FastHttpLocust):
    host = ''
    task_set = PressureTest
    wait_time = between(0.0, 0.0)
