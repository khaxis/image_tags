#!/usr/bin/env python
from flask import Flask
from flask import render_template
from flask import url_for
from flask import request
app = Flask(__name__)


def urls_for():
    url_for('static', filename='style.css')
    url_for('static', filename='table.css')
    url_for('static', filename='gallery.css')
    url_for('static', filename='base_elements.css')
