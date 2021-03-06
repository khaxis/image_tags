import io
import cv2
import numpy as np
from utils.file_handler import get_file_stream


def get_image(image_path, cv2_img_flag=0):
    """Get OpenCV like image"""
    img_array = np.asarray(bytearray(get_file_stream(image_path).read()), dtype=np.uint8)
    if len(img_array):
        return cv2.imdecode(img_array, cv2_img_flag)
    return None

def is_valid_image(fp, cv2_img_flag=0):
    img_array = np.asarray(bytearray(fp.read()))
    image = None
    if len(img_array):
        image = cv2.imdecode(img_array, cv2_img_flag)
    fp.seek(0)
    return image is not None

def resize_image_by_side(fp, side_size, cv2_img_flag=0):
    img_array = np.asarray(bytearray(fp.read()))
    side_size = float(side_size)
    fp.seek(0)
    if len(img_array):
        image = cv2.imdecode(img_array, cv2_img_flag)
        ratio = max(side_size / image.shape[0], side_size / image.shape[1])
        image = cv2.resize(image, (0,0), fx=ratio, fy=ratio)
        encoded = cv2.imencode('.jpeg', image)[1]
        fp = io.BytesIO(encoded)
    return fp