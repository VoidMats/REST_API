#! /usr/bin/python3

from os import environ
from app import create_app

run_mode = environ.get('RUN_MODE') or "testing"
app = create_app(config_name=run_mode)