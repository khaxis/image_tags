#!/usr/bin/env python
import sys
import argparse
from utils import img_collection as icoll
from utils import progress_bar
import random
from features.bowSift100.bowSift100 import BOWSift100



def parseArguments():
	parser = argparse.ArgumentParser(description='Make learning pool')
	parser.add_argument('--description', dest='description', help='Name of the pool', required=True)
	parser.add_argument('--capacity', dest='capacity', help='Number of random samples', required=True)

	return parser.parse_args()


def makePool(argv):
	#args = parseArguments()
	imageUrls = []
	return BOWSift100()
	


if __name__ == "__main__":
	print makePool(sys.argv)