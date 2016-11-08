from features.baseSlice.baseSlice import BaseSlice
from utils import img_collection as icoll
import cv2
import numpy as np
from sklearn.externals import joblib
from scipy.cluster.vq import *
from sklearn.preprocessing import StandardScaler


class BOWSift100(BaseSlice):
	def __init__(self):
		print "init"


	def getVersion(self, input):
		"""Get a version number as int"""
		return 0


	def extract(self, images):
		"""Extract features of the given images"""
		return None
