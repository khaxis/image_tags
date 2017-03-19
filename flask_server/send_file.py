#!/usr/bin/env python
from flask_server.common import *
from flask_server.pool import *
from os.path import join
from utils.config import getDataPath


@app.route("/get_image/<image_path>")
def get_image(image_path):
    return send_from_directory(join(getDataPath(), 'images'), image_path)
