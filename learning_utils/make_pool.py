#!/usr/bin/env python
import sys
import argparse
from utils import img_collection as icoll
from utils import pool_collection as pcoll
from utils import progress_bar
import random

PREVIEW_COUNT = 100

def parseArguments():
    parser = argparse.ArgumentParser(description='Make learning pool')
    parser.add_argument('--target', dest='target', help='Target class', required=True)
    parser.add_argument('--out', help='File pool-id will be written to')
    parser.add_argument('--test-mode', help='Do nothing, but return prepared pool', action='store_true')

    return parser.parse_args()


def makePool(argv):
    args = parseArguments()
    if args.test_mode:
        if args.out:
            with open(args.out, 'w') as f:
                f.write('589cb3d60310e95ec7728f63')
        return

    tree = icoll.findChildren(args.target)
    print("Tree of positives:")
    icoll.printTree(tree, depth=1)

    sys.stdout.write("Fetching urls... ")
    sys.stdout.flush()
    image_urls_positives = icoll.getFlattenUrlsTree(tree)
    sys.stdout.write("Done\n")

    description = "%s %s" % (tree['NId'], tree['description'])
    poolId = pcoll.makePool(description)
    sys.stdout.write("Pool created with ID: %s\n" % poolId)
    
    image_urls_positives_size = len(image_urls_positives)
    preview_prob = float(PREVIEW_COUNT) / image_urls_positives_size
    print("Assigning positives")
    for index, row in zip(range(image_urls_positives_size), image_urls_positives):
        icoll.assignToPool(row, poolId, 1, random.random() < preview_prob)
        progress_bar.printProgress(index + 1, image_urls_positives_size)

    parents = icoll.findParents(args.target)

    image_urls_negatives = []
    if len(parents) > 0:
        directParent = parents[0]
        print(("Direct parent node: %s %s" % (directParent['NId'], directParent['description'])))
        tree_negatives = icoll.findChildren(directParent['NId'], maxDepth=1, excludeNIds=[args.target])
        print("Negatives tree:")
        icoll.printTree(tree_negatives, depth=1)
        image_urls_negatives = icoll.getFlattenUrlsTree(tree_negatives)
        if len(image_urls_negatives) > image_urls_positives_size:
            image_urls_negatives = random.sample(image_urls_negatives, image_urls_positives_size)
        print(("Added %d samples from sibling branches" % len(image_urls_negatives)))

    # Add extra random negatives
    for row in icoll.findRandomImageUrlsDocuments(image_urls_positives_size):
        image_urls_negatives.append(row)

    print("Assigning negatives")
    image_urls_negatives_size = len(image_urls_negatives)
    preview_prob = float(PREVIEW_COUNT) / image_urls_negatives_size
    for index, row in zip(range(image_urls_negatives_size), image_urls_negatives):
        icoll.assignToPool(row, poolId, 0, random.random() < preview_prob)
        progress_bar.printProgress(index + 1, image_urls_negatives_size)

    if args.out:
        with open(args.out, 'w') as f:
            f.write(str(poolId))


if __name__ == "__main__":
    makePool(sys.argv)
