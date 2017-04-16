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
    image = cv2.imdecode(np.asarray(bytearray(fp.read())), cv2_img_flag)
    fp.seek(0)
    return image is not None