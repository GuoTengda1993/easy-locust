# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    host = db.Column(db.String(255))
    min_wait = db.Column(db.Float, default=0)
    max_wait = db.Column(db.Float, default=0)
    request_mode = db.Column(db.String(20), default="FastHttpLocust")
    token = db.Column(db.Boolean, default=False)
    run_in_order = db.Column(db.Boolean, default=False)
    content_type = db.Column(db.String(30), default="application/json")
    headers = db.Column(db.Text)


class ApiData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    config_id = db.Column(db.Integer, db.ForeignKey("config.id"))
    weight = db.Column(db.Integer, default=100)
    url = db.Column(db.String(256), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    query = db.Column(db.Text)
    request_data = db.Column(db.Text)
    expect_status_code = db.Column(db.Integer)
    expect_str = db.Column(db.Text)
    extra = db.Column(db.Text)
    status = db.Column(db.Integer, default=1)  # 0: disable, 1: enable

    config = db.relationship("Config", back_populates="apis")


class Slave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(256), nullable=False)
    status = db.Column(db.Integer, default=1)  # 0: disable, 1: enable, 2: checked
    category = db.Column(db.String(20), default="locust")  # locust or boomer... This column will be used in the future
    extra = db.Column(db.String(255))


# class Auth(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     config_id = db.Column(db.Integer, db.ForeignKey("config.id"))
#     method = db.Column(db.String(10), default="POST")
#     token_utl = db.Column(db.String(256), nullable=False)
#     content_type = db.Column(db.String(30), default="application/json")
#     body = db.Column(db.Text)
#     header_key = db.Column(db.String(20), default="x-auth-token")
#     token_index = db.Column(db.Text)  # Header: X-subject-Token  or JSON: body.token
#
#     config = db.relationship("Config", back_populates="auths")
