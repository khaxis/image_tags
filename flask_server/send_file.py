#!/usr/bin/env python
from common import *
from pool import *
from os.path import join
from utils.config import getDataPath


@app.route("/get_image/<image_path>")
def get_image(image_path):
	return send_from_directory(join(getDataPath(), 'data/images'), image_path)
