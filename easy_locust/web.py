# -*- coding: utf-8 -*-
import json

from flask import request, render_template
from flask_restful import Resource, Api
from easy_locust.models import app, db, Config, Url, Slave

from easy_locust.util.ssh_agent import SSHAgent
from paramiko.ssh_exception import AuthenticationException


Methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD']


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
            return {'msg': 'request_mode should be FastHttpLocust or HttpLocust', 'code': 210}, 210
        if max_wait < min_wait:
            return {'msg': 'max-wait cannot smaller than min-wait', 'code': 210}, 210
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
            msg, code = "Add config fail: {}".format(e), 210
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
            msg, code = "Edit config fail: {}".format(e), 210
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
            "ip": slave.ip,
            "username": slave.username,
            "password": slave.password,
            "status": slave.status
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
            "ip": slave.ip,
            "username": slave.username,
            "password": slave.password,
            "status": slave.status
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
            msg, code = "Add slave node fail: {}".format(e), 210
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
            msg, code = "Edit slave node fail: {}".format(e), 210
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


class SlaveOp(Resource):

    def get(self, id, operation):
        slave = Slave.query.filter_by(id=id).first_or_404()
        if operation == 'disable':
            if slave.status == 0:
                return {'msg': 'This slave is disabled already', 'code': 210}, 210
            slave.status = 0
            msg, code = 'success', 200
        elif operation == 'enable':
            if slave.status == 1:
                return {'msg': 'This slave is enabled already', 'code': 210}, 210
            try:
                ssh = SSHAgent(ip=slave.ip, username=slave.username, password=slave.password)
                slave.status = 1
                msg, code = 'success', 200
            except AuthenticationException:
                msg, code = 'Authentication error with this slave', 210
            finally:
                ssh.close()
        elif operation == 'check':
            if slave.status == 2:
                return {'msg': 'This slave is checked already', 'code': 210}, 210
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
            return {'msg': 'No such action', 'code': 404}, 404
        db.session.commit()
        return {'msg': msg, 'code': code}, code


class APIList(Resource):

    def get(self):
        apis = Url.query.order_by(Url.id).all()
        data = [{
            "id": api.id,
            "name": api.name,
            "config_id": api.config_id,
            "weight": api.weight,
            "url": api.url,
            "method": api.method,
            "query": api.query,
            "request_data": api.request_data,
            "expect_status_code": api.expect_status_code,
            "expect_str": api.expect_str,
            "status": api.status
        } for api in apis]
        response = {
            "msg": "success",
            "code": 200,
            "res": data
        }
        return response, 200


class APIManage(Resource):

    def get(self, id):
        api = Url.query.filter_by(id=id).first_or_404()
        data = {
            "id": api.id,
            "name": api.name,
            "config_id": api.config_id,
            "weight": api.weight,
            "url": api.url,
            "method": api.method,
            "query": api.query,
            "request_data": api.request_data,
            "expect_status_code": api.expect_status_code,
            "expect_str": api.expect_str,
            "status": api.status
        }
        response = {
            "msg": "success",
            "code": 200,
            "res": data
        }
        return response, 200

    def post(self):
        data = request.json
        if data.get('method') not in Methods:
            msg, code = "method error", 210
        else:
            extra = json.dumps(data, ensure_ascii=False, indent=4)
            try:
                api = Url(extra=extra, **data)
                db.session.add(api)
                db.session.commit()
                msg, code = "success", 201
            except Exception as e:
                msg, code = "Add api fail: {}".format(e), 210
        response = {
            "msg": msg,
            "code": code,
            "res": ""
        }
        return response, code

    def put(self, id):
        api = Url.query.filter_by(id=id).first_or_404()
        data = request.json
        if data.get('method') not in Methods:
            msg, code = "method error", 210
        else:
            try:
                extra = json.loads(api.extra, encoding='utf-8')
                for key, value in data.items():
                    setattr(api, key, value)
                    extra[key] = value
                api.extra = extra
                db.session.commit()
                msg, code = "success", 200
            except Exception as e:
                msg, code = "Edit slave node fail: {}".format(e), 210
        response = {
            "msg": msg,
            "code": code,
            "res": ""
        }
        return response, code

    def delete(self, id):
        api = Url.query.filter_by(id=id).first_or_404()
        db.session.delete(api)
        db.session.commit()
        response = {
            "msg": "success",
            "code": 204,
            "res": ""
        }
        return response, 204


class APIOp(Resource):

    def get(self, id, operation):
        api = Url.query.filter_by(id=id).first_or_404()
        if operation == 'enable':
            if api.status == 1:
                return {'msg': 'This api is enabled already', 'code': 210}, 210
            api.status = 1
        elif operation == 'disable':
            if api.status == 0:
                return {'msg': 'This api is disabled already', 'code': 210}, 210
            api.status = 0
        else:
            return {'msg': 'No such action', 'code': 404}, 404
        db.session.commit()
        return {'msg': 'success', 'code': 200}, 200


@app.route('/', methods=['GET'])
def start():
    config = Config.query.first()
    # apis = Url.query.order_by(Url.id.desc()).all()
    slaves = Slave.query.order_by(Slave.id.desc()).all()
    return render_template("index.html", config=config, apis=None, slaves=slaves)


def register_apis(api_reg):
    api_reg.add_resource(ConfigList, '/config/list')
    api_reg.add_resource(ConfigManage, '/config', '/config/<id>')
    api_reg.add_resource(SlaveList, '/slave/list')
    api_reg.add_resource(SlaveManage, '/slave', '/slave/<id>')
    api_reg.add_resource(SlaveOp, '/slave/<id>/<operation>')
    api_reg.add_resource(APIList, '/api/list')
    api_reg.add_resource(APIManage, '/api', '/api/<id>')
    api_reg.add_resource(APIOp, '/api/<id>/<operation>')


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
        # apis = Url.query.order_by(Url.id.desc()).all()
        slaves = Slave.query.order_by(Slave.id.desc()).all()
        return dict(config=config, apis=None, slaves=slaves)


def init_app(port=8899, debug=False, threaded=True):
    api_reg = Api(app)
    register_db()
    register_apis(api_reg)
    # register_template_context(app)
    app.run(host='0.0.0.0', port=port, debug=debug, threaded=threaded)
