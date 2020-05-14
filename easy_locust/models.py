# -*- coding: utf-8 -*-
import sys
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = prefix + os.path.join(basedir, 'easy-locust.sqlite')
template_path = os.path.join(basedir, 'templates')
static_path = os.path.join(basedir, 'static')

app = Flask('easy-locust', template_folder=template_path, static_folder=static_path)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = db_path
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SECRET_KEY'] = 'easy-locust-is-nice'
app.config['CSRF_ENABLED'] = True

db = SQLAlchemy(app)


class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    host = db.Column(db.String(255))
    min_wait = db.Column(db.Float, default=0)
    max_wait = db.Column(db.Float, default=0)
    request_mode = db.Column(db.String(20), default="FastHttpLocust")
    token = db.Column(db.Integer, default=0)
    run_in_order = db.Column(db.Integer, default=0)
    content_type = db.Column(db.String(30), default="application/json")
    headers = db.Column(db.Text)


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    weight = db.Column(db.Integer, default=100)
    url = db.Column(db.String(256), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    query_params = db.Column(db.Text)
    request_data = db.Column(db.Text)
    expect_status_code = db.Column(db.Integer)
    expect_str = db.Column(db.Text)
    extra = db.Column(db.Text)
    status = db.Column(db.Integer, default=1)  # 0: disable, 1: enable


class Slave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(128), nullable=False)
    username = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(256), nullable=False)
    status = db.Column(db.Integer, default=1)  # 0: disable, 1: enable, 2: checked
    category = db.Column(db.String(20), default="locust")  # locust or boomer... This column will be used in the future
    extra = db.Column(db.String(255))
