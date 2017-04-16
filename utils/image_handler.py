import cv2
import numpy as np
from utils.file_handler import get_stream

def get_image(image_path, cv2_img_flag=0):
    """Get OpenCV like image"""
    img_array = np.asarray(bytearray(get_stream(image_path)), dtype=np.uint8)
    return cv2.imdecode(img_array, cv2_img_flag)
