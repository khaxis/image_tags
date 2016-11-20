#!/usr/bin/env python
import sys
import argparse
from utils import img_collection as icoll
from utils import web_utils
from utils import progress_bar
from features import sliceFactory
import random
import os
import cv2

def parseArguments():
	parser = argparse.ArgumentParser(description='Fetch all urls from the pool')
	parser.add_argument('--pool', dest='pool', help='Pool id', required=True)

	return parser.parse_args()


def fetchPool(argv):
	args = parseArguments()
	
	workingDir = os.getcwd()
	storePath = os.path.join(workingDir, 'data', 'images')

	i = 0
	totalCount = icoll.getPoolSize(args.pool)
	
	for row in icoll.getPoolUrlsIterator(args.pool):
		### !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
		break
		destination = os.path.join(storePath, row['IId'])
		if 'path' not in row:
			if web_utils.downloadSingleImage(row['Url'], destination):
				# the image successfully saved
				icoll.updateImagePath(row, destination)
				icoll.updateImageDownloadableStatus(row, True)
			else:
				icoll.updateImageDownloadableStatus(row, False)
		i += 1
		progress_bar.printProgress(i, totalCount)
	print

	print "Pool cached"
	print "Extracting features..."

	i = 0
	extractors = sliceFactory.getExtractors()
	for row in icoll.getPoolUrlsIterator(args.pool):
		if 'path' in row and row['downloadable']:
			im = cv2.imread(row['path'])
			slices = {}
			for extractor in extractors:
				features = extractor.extract(im)
				if features[0] is not None:
					entry = {}
					entry['features'] = features[0][0].tolist()
					entry['version'] = extractor.getVersion()
					slices[extractor.getName()] = entry
					
			if len(slices) > 0:
				icoll.updateImageSlices(row, slices)
		i += 1
		progress_bar.printProgress(i, totalCount)
	print	

	return


if __name__ == "__main__":
	fetchPool(sys.argv)