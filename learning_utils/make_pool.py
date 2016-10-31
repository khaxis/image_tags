#!/usr/bin/env python
import sys
import argparse
from utils import img_collection as icoll
from utils import progress_bar
import random


def parseArguments():
	parser = argparse.ArgumentParser(description='Make learning pool')
	parser.add_argument('--target', dest='target', help='Target class', required=True)

	return parser.parse_args()


def makePool(argv):
	args = parseArguments()

	tree = icoll.findChildren(args.target)
	print "Tree of positives:"
	icoll.printTree(tree, depth=1)

	sys.stdout.write("Fetching urls... ")
	sys.stdout.flush()
	image_urls_positives = icoll.getFlattenUrlsTree(tree)
	sys.stdout.write("Done\n")

	description = "%s %s" % (tree['NId'], tree['description'])
	description = "test"
	poolId = icoll.makePool(description)
	sys.stdout.write("Pool created with ID: %s\n" % poolId)
	
	image_urls_positives_size = len(image_urls_positives)

	print "Assigning positives"
	for index, row in zip(range(image_urls_positives_size), image_urls_positives):
		icoll.assignToPool(row, poolId, 1)
		progress_bar.printProgress(index + 1, image_urls_positives_size)

	parents = icoll.findParents(args.target)

	image_urls_negatives = []
	if len(parents) > 0:
		directParent = parents[0]
		print "Direct parent node: %s %s" % (directParent['NId'], directParent['description'])
		tree_negatives = icoll.findChildren(directParent['NId'], maxDepth=1, excludeNIds=[args.target])
		print "Negatives tree:"
		icoll.printTree(tree_negatives, depth=1)
		image_urls_negatives = icoll.getFlattenUrlsTree(tree_negatives)
		if len(image_urls_negatives) > image_urls_positives_size:
			image_urls_negatives = random.sample(image_urls_negatives, image_urls_positives_size)
		print "Added %d samples from sibling branches" % len(image_urls_negatives)

	# Add extra random negatives
	for row in icoll.findRandomImageUrlsDocuments(image_urls_positives_size):
		image_urls_negatives.append(row)

	print "Assigning negatives"
	image_urls_negatives_size = len(image_urls_negatives)
	for index, row in zip(range(image_urls_negatives_size), image_urls_negatives):
		icoll.assignToPool(row, poolId, 0)
		progress_bar.printProgress(index + 1, image_urls_negatives_size)

	return poolId


if __name__ == "__main__":
	makePool(sys.argv)