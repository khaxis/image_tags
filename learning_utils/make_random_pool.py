#!/usr/bin/env python
import sys
import argparse
from utils import img_collection as icoll
from utils import progress_bar
import random


def parseArguments():
    parser = argparse.ArgumentParser(description='Make learning pool')
    parser.add_argument('--description', dest='description', help='Name of the pool', required=True)
    parser.add_argument('--capacity', dest='capacity', help='Number of random samples', required=True)

    return parser.parse_args()


def makePool(argv):
    args = parseArguments()
    imageUrls = []

    poolId = icoll.makePool(args.description)
    print "Getting random images..."
    for row in icoll.findRandomImageUrlsDocuments(args.capacity):
        imageUrls.append(row)

    print "Assigning images to the pool"
    imageUrlsSize = len(imageUrls)
    for index, row in enumerate(imageUrls, 1):
        icoll.assignToPool(row, poolId, 1)
        progress_bar.printProgress(index, imageUrlsSize)

    return poolId


if __name__ == "__main__":
    print makePool(sys.argv)
