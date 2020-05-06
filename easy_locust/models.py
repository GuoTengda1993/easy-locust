# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    host = db.Column(db.Integer, nullable=False)
    min_wait = db.Column(db.Float, default=0)
    max_wait = db.Column(db.Float, default=0)
    request_mode = db.Column(db.String(20), default="FastHttpLocust")
    token = db.Column(db.Boolean, default=False)
    run_in_order = db.Column(db.Boolean, default=False)
    content_type = db.Column(db.String(30), default="application/json")
    headers = db.Column(db.Text)


class Auth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    config_id = db.Column(db.Integer, db.ForeignKey("config.id"))
    method = db.Column(db.String(10), default="POST")
    token_utl = db.Column(db.String(256), nullable=False)
    content_type = db.Column(db.String(30), default="application/json")
    body = db.Column(db.Text)
    header_key = db.Column(db.String(20), default="x-auth-token")
    token_index = db.Column(db.Text)  # Header: X-subject-Token  or JSON: body.token

    config = db.relationship("Config", back_populates="auths")


class Api(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    config_id = db.Column(db.Integer, db.ForeignKey("config.id"))
    weight = db.Column(db.Integer, default=100)
    url = db.Column(db.String(256))
    method = db.Column(db.String(10), default="GET")
    query = db.Column(db.Text)
    request_data = db.Column(db.Text)
    expect_status_code = db.Column(db.Integer)
    expect_str = db.Column(db.Text)

    config = db.relationship("Config", back_populates="apis")


class Slave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(256), nullable=False)
