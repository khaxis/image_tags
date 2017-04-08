#!/usr/bin/env python
from flask import send_file
from flask_server.pool import *
from os.path import join
from utils.config import getDataPath
import io

from boto import storage_uri
from gcs_oauth2_boto_plugin import oauth2_plugin


@app.route("/get_image/<image_path>")
def get_image(image_path):
    root = 'gs://image_tags/images/'
    content = storage_uri(root + image_path)
    image_file = io.BytesIO()
    content.get_contents_to_file(image_file)
    image_file.seek(0)
    return send_file(image_file, attachment_filename=image_path, as_attachment=False)
