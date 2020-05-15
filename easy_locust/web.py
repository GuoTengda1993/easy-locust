# -*- coding: utf-8 -*-
import json
from functools import wraps

from flask import request, render_template
from flask_restful import Resource, Api
from easy_locust.models import app, db, Config, Test, Slave

from easy_locust.util.ssh_agent import SSHAgent
from paramiko.ssh_exception import AuthenticationException


Methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD']


def format_response(func):
    @wraps(func)
    def formatter(*args, **kwargs):
        p = func(*args, **kwargs)
        if len(p) == 2:
            msg, code = p
            res = None
        else:
            msg, res, code = p
        _response = {
            "msg": msg,
            "res": res,
            "code": code
        }
        return _response, code
    return formatter


class ConfigList(Resource):

    @format_response
    def get(self):
        configs = Config.query.order_by(Config.id).all()
        res = [{
            "host": config.host,
            "min_wait": config.min_wait,
            "max_wait": config.max_wait,
            "request_mode": config.request_mode,
            "get_token": config.token,
            "run_in_order": config.run_in_order,
            "content_type": config.content_type
        } for config in configs]
        return "success", res, 200


class ConfigManage(Resource):

    @format_response
    def get(self, id):
        config = Config.query.filter_by(id=id).first_or_404()
        res = {
            "host": config.host,
            "min_wait": config.min_wait,
            "max_wait": config.max_wait,
            "request_mode": config.request_mode,
            "get_token": config.token,
            "run_in_order": config.run_in_order,
            "content_type": config.content_type
        }
        return "success", res, 200

    @format_response
    def post(self):
        data = request.json
        min_wait = float(data.get('min_wait', 0.0))
        max_wait = float(data.get('max_wait', 0.0))
        token = bool(data.get('token', False))
        run_in_order = bool(data.get('run_in_order', False))
        request_mode = data.get('request_mode')
        if request_mode not in ['FastHttpLocust', 'HttpLocust']:
            return 'request_mode should be FastHttpLocust or HttpLocust', 210
        if max_wait < min_wait:
            return 'max-wait cannot smaller than min-wait', 210
        data['min_wait'] = min_wait
        data['max_wait'] = max_wait
        data['token'] = token
        data['run_in_order'] = run_in_order
        try:
            config = Config(**data)
            db.session.add(config)
            db.session.commit()
            return "success", 201
        except Exception as e:
            return "Add config fail: {}".format(e), 210

    @format_response
    def put(self, id):
        config = Config.query.filter_by(id=id).first_or_404()
        data = request.json
        try:
            for key, value in data.items():
                setattr(config, key, value)
            db.session.commit()
            return "success", 200
        except Exception as e:
            return "Edit config fail: {}".format(e), 210

    @format_response
    def delete(self, id):
        config = Config.query.filter_by(id=id).first_or_404()
        db.session.delete(config)
        db.session.commit()
        return "success", 204


class SlaveList(Resource):

    @format_response
    def get(self):
        slaves = Slave.query.order_by(Slave.id).all()
        res = [{
            "id": slave.id,
            "ip": slave.ip,
            "username": slave.username,
            "password": slave.password,
            "status": slave.status
        } for slave in slaves]
        return "success", res, 200


class SlaveManage(Resource):

    @format_response
    def get(self, id):
        slave = Slave.query.filter_by(id=id).first_or_404()
        res = {
            "id": slave.id,
            "ip": slave.ip,
            "username": slave.username,
            "password": slave.password,
            "status": slave.status
        }
        return "success", res, 200

    @format_response
    def post(self):
        data = request.json
        try:
            slave = Slave(**data)
            db.session.add(slave)
            db.session.commit()
            return "success", 201
        except Exception as e:
            return "Add slave node fail: {}".format(e), 210

    @format_response
    def put(self, id):
        slave = Slave.query.filter_by(id=id).first_or_404()
        data = request.json
        try:
            for key, value in data.items():
                setattr(slave, key, value)
            db.session.commit()
            return "success", 200
        except Exception as e:
            return "Edit slave node fail: {}".format(e), 210

    @format_response
    def delete(self, id):
        slave = Slave.query.filter_by(id=id).first_or_404()
        db.session.delete(slave)
        db.session.commit()
        return "success", 204


class SlaveOp(Resource):

    @format_response
    def get(self, id, operation):
        slave = Slave.query.filter_by(id=id).first_or_404()
        if operation == 'disable':
            if slave.status == 0:
                return 'This slave is disabled already', 210
            slave.status = 0
            msg, code = 'success', 200
        elif operation == 'enable':
            if slave.status == 1:
                return 'This slave is enabled already', 210
            try:
                ssh = SSHAgent(ip=slave.ip, username=slave.username, password=slave.password)
                ssh.close()
                slave.status = 1
                msg, code = 'success', 200
            except AuthenticationException:
                return 'Authentication error with this slave', 210
        elif operation == 'check':
            if slave.status == 2:
                return 'This slave is checked already', 210
            ssh = SSHAgent(ip=slave.ip, username=slave.username, password=slave.password)
            with ssh:
                check = ssh.check_locust()
            if check:
                slave.status = 2
                msg, code = 'success', 200
            else:
                slave.status = 0
                msg, code = 'Cannot install locustio==0.14.6, please install it manually.', 210
                slave.extra = msg
        else:
            return 'No such action', 404
        db.session.commit()
        return msg, code


class TestList(Resource):

    @format_response
    def get(self):
        apis = Test.query.order_by(Test.id).all()
        res = [{
            "id": test.id,
            "name": test.name,
            "config_id": test.config_id,
            "weight": test.weight,
            "url": test.url,
            "method": test.method,
            "query_params": test.query_params,
            "request_data": test.request_data,
            "expect_status_code": test.expect_status_code,
            "expect_str": test.expect_str,
            "status": test.status
        } for test in apis]
        return "success", res, 200


class TestManage(Resource):

    @format_response
    def get(self, id):
        test = Test.query.filter_by(id=id).first_or_404()
        res = {
            "id": test.id,
            "name": test.name,
            "config_id": test.config_id,
            "weight": test.weight,
            "url": test.url,
            "method": test.method,
            "query_params": test.query_params,
            "request_data": test.request_data,
            "expect_status_code": test.expect_status_code,
            "expect_str": test.expect_str,
            "status": test.status
        }
        return "success", res, 200

    @format_response
    def post(self):
        data = request.json
        if data.get('method') not in Methods:
            return "method error", 210
        extra = json.dumps(data, ensure_ascii=False, indent=4)
        try:
            test = Test(extra=extra, **data)
            db.session.add(test)
            db.session.commit()
            return "success", 201
        except Exception as e:
            return "Add test fail: {}".format(e), 210

    @format_response
    def put(self, id):
        test = Test.query.filter_by(id=id).first_or_404()
        raw_data = request.json
        data = json.loads(raw_data, encoding='utf-8')
        if data.get('method') not in Methods:
            return "method error", 210
        try:
            for key, value in data.items():
                setattr(test, key, value)
            test.extra = raw_data
            db.session.commit()
            return "success", 200
        except Exception as e:
            return "Edit fail: {}".format(e), 210

    @format_response
    def delete(self, id):
        test = Test.query.filter_by(id=id).first_or_404()
        db.session.delete(test)
        db.session.commit()
        return "success", 204


class TestOp(Resource):

    @format_response
    def get(self, id, operation):
        test = Test.query.filter_by(id=id).first_or_404()
        if operation == 'enable':
            if test.status == 1:
                return 'This test is enabled already', 210
            test.status = 1
        elif operation == 'disable':
            if test.status == 0:
                return 'This test is disabled already', 210
            test.status = 0
        else:
            return 'No such action', 404
        db.session.commit()
        return 'success', 200


@app.route('/', methods=['GET'])
def start():
    config = Config.query.first()
    apis = Test.query.order_by(Test.id.desc()).all()
    slaves = Slave.query.order_by(Slave.id.desc()).all()
    return render_template("index.html", config=config, apis=apis, slaves=slaves)


def register_apis(api_reg):
    api_reg.add_resource(ConfigList, '/config/list')
    api_reg.add_resource(ConfigManage, '/config', '/config/<id>')
    api_reg.add_resource(SlaveList, '/slave/list')
    api_reg.add_resource(SlaveManage, '/slave', '/slave/<id>')
    api_reg.add_resource(SlaveOp, '/slave/<id>/<operation>')
    api_reg.add_resource(TestList, '/test/list')
    api_reg.add_resource(TestManage, '/test', '/test/<id>')
    api_reg.add_resource(TestOp, '/test/<id>/<operation>')


def register_db():
    db.create_all()
    config = Config.query.filter_by(id=1).first()
    if not config:
        config = Config(name="defaultConfig")
        db.session.add(config)
        db.session.commit()


def register_template_context(app):
    @app.context_processor
    def make_template_context():
        config = Config.query.first()
        apis = Test.query.order_by(Test.id.desc()).all()
        slaves = Slave.query.order_by(Slave.id.desc()).all()
        return dict(config=config, apis=apis, slaves=slaves)


def init_app(port=8899, debug=False, threaded=True):
    api_reg = Api(app)
    register_db()
    register_apis(api_reg)
    # register_template_context(app)
    app.run(host='0.0.0.0', port=port, debug=debug, threaded=threaded)
