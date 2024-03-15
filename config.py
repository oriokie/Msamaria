#config.py
# -*- coding: utf-8 -*-
# Configuration file for the Flask application
import os
basedir = os.path.abspath(os.path.dirname(__file__))
class Config(object):
    SECRET_KEY = '3d6f45a5fc12445dbac2f59c3b6c7cb1'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///benevolent.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    TESTING = True
    WTF_CSRF_ENABLED = False
    