# -*- coding: utf-8 -*-
from flask import request
from flask_restful import Resource

from .models import *


class ConfigList(Resource):

    def get(self):
        configs = Config.query.order_by(Config.id).all()
        data = [{
            "host": config.host,
            "min_wait": config.min_wait,
            "max_wait": config.max_wait,
            "request_mode": config.request_mode,
            "get_token": config.token,
            "run_in_order": config.run_in_order,
            "content_type": config.content_type
        } for config in configs]
        response = {
            "msg": "success",
            "code": 200,
            "res": data
        }
        return response, 200


class ConfigManage(Resource):

    def get(self, id):
        config = Config.query.filter_by(id=id).first_or_404()
        data = {
            "host": config.host,
            "min_wait": config.min_wait,
            "max_wait": config.max_wait,
            "request_mode": config.request_mode,
            "get_token": config.token,
            "run_in_order": config.run_in_order,
            "content_type": config.content_type
        }
        response = {
            "msg": "success",
            "code": 200,
            "res": data
        }
        return response, 200

    def post(self):
        data = request.json
        min_wait = float(data.get('min_wait', 0.0))
        max_wait = float(data.get('max_wait', 0.0))
        token = bool(data.get('token', False))
        run_in_order = bool(data.get('run_in_order', False))
        request_mode = data.get('request_mode')
        if request_mode not in ['FastHttpLocust', 'HttpLocust']:
            return {'msg': 'request_mode should be FastHttpLocust or HttpLocust', 'code': 400}, 400
        if max_wait < min_wait:
            return {'msg': 'max-wait cannot smaller than min-wait', 'code': 400}, 400
        data['min_wait'] = min_wait
        data['max_wait'] = max_wait
        data['token'] = token
        data['run_in_order'] = run_in_order
        try:
            config = Config(**data)
            db.session.add(config)
            db.session.commit()
            msg, code = "success", 201
        except Exception as e:
            msg, code = "Add config fail: {}".format(e), 400
        response = {
            "msg": msg,
            "code": code,
            "res": ""
        }
        return response, code

    def put(self, id):
        config = Config.query.filter_by(id=id).first_or_404()
        data = request.json
        try:
            for key, value in data.items():
                setattr(config, key, value)
            db.session.commit()
            msg, code = "success", 200
        except Exception as e:
            msg, code = "Edit config fail: {}".format(e), 400
        response = {
            "msg": msg,
            "code": code,
            "res": ""
        }
        return response, code

    def delete(self, id):
        config = Config.query.filter_by(id=id).first_or_404()
        db.session.delete(config)
        db.session.commit()
        response = {
            "msg": "success",
            "code": 204,
            "res": ""
        }
        return response, 204


class SlaveList(Resource):

    def get(self):
        slaves = Slave.query.order_by(Slave.id).all()
        data = [{
            "id": slave.id,
            "username": slave.username,
            "password": slave.password
        } for slave in slaves]
        response = {
            "msg": "success",
            "code": 200,
            "res": data
        }
        return response, 200


class SlaveManage(Resource):

    def get(self, id):
        slave = Slave.query.filter_by(id=id).first_or_404()
        data = {
            "id": slave.id,
            "username": slave.username,
            "password": slave.password
        }
        response = {
            "msg": "success",
            "code": 200,
            "res": data
        }
        return response, 200

    def post(self):
        data = request.json
        try:
            slave = Slave(**data)
            db.session.add(slave)
            db.session.commit()
            msg, code = "success", 201
        except Exception as e:
            msg, code = "Add slave node fail: {}".format(e), 400
        response = {
            "msg": msg,
            "code": code,
            "res": ""
        }
        return response, code

    def put(self, id):
        slave = Slave.query.filter_by(id=id).first_or_404()
        data = request.json
        try:
            for key, value in data.items():
                setattr(slave, key, value)
            db.session.commit()
            msg, code = "success", 200
        except Exception as e:
            msg, code = "Edit slave node fail: {}".format(e), 400
        response = {
            "msg": msg,
            "code": code,
            "res": ""
        }
        return response, code

    def delete(self, id):
        slave = Slave.query.filter_by(id=id).first_or_404()
        db.session.delete(slave)
        db.session.commit()
        response = {
            "msg": "success",
            "code": 204,
            "res": ""
        }
        return response, 204


class APIList(Resource):

    def get(self):
        apis = Api.query.order_by(Api.id).all()
        data = [{
            "id": api.id,
            "config_id": api.config_id,
            "weight": api.weight,
            "url": api.url,
            "method": api.method,
            "query": api.query,
            "request_data": api.request_data,
            "expect_status_code": api.expect_status_code,
            "expect_str": api.expect_str
        } for api in apis]
        response = {
            "msg": "success",
            "code": 200,
            "res": data
        }
        return response, 200


class APIManage(Resource):

    def get(self, id):
        pass
