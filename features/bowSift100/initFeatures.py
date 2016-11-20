#!/usr/bin/env python
import sys
import argparse
from utils import img_collection as icoll
from utils import progress_bar
import cv2
import numpy as np
from sklearn.externals import joblib
from scipy.cluster.vq import *
from sklearn.preprocessing import StandardScaler


def parseArguments():
	parser = argparse.ArgumentParser(description='Using available pool create BOW dictionary')
	parser.add_argument('--pool', dest='pool', help='Pool id', required=True)
	parser.add_argument('--output', dest='output', help='The output .pickle file', default='out.pkl')

	return parser.parse_args()


def createDictionary(argv):
	args = parseArguments()
	
	trainPool = []
	for i, row in enumerate(icoll.getPoolUrlsIterator(args.pool)):
		if row['downloadable']:
			trainPool.append(row)
	sys.stdout.write("Pool size: %d\n" % len(trainPool))

	# Create feature extraction and keypoint detector objects
	fea_det = cv2.FeatureDetector_create("SIFT")
	des_ext = cv2.DescriptorExtractor_create("SIFT")

	# List where all the descriptors are stored
	des_list = []

	for imageRow in trainPool:
		im = cv2.imread(imageRow['path'])
		if im is None:
			continue
		kpts = fea_det.detect(im)
		kpts, des = des_ext.compute(im, kpts)
		des_list.append(des)

	# Stack all the descriptors vertically in a numpy array
	descriptors = des_list[0][1]
	for descriptor in des_list[1:]:
		descriptors = np.vstack((descriptors, descriptor))

	# Perform k-means clustering
	sys.stdout.write("Perform k-means clustering... ")
	sys.stdout.flush()
	k = 100
	voc, variance = kmeans(descriptors, k, 1)
	sys.stdout.write("done\n")

	imFeatures = np.zeros((len(des_list), k), "float32")
	for i in xrange(len(des_list)):
		words, distance = vq(des_list[i],voc)
		for w in words:
			imFeatures[i][w] += 1

	# Scaling the words
	stdSlr = StandardScaler().fit(imFeatures)
	joblib.dump((stdSlr, k, voc), args.output, compress=3)

	sys.stdout.write("Result stored in args.output\n")

	return 0


if __name__ == "__main__":
	sys.exit(createDictionary(sys.argv))