#!/usr/bin/env python
import sys
import argparse
from utils import img_collection as icoll
from utils import progress_bar
from utils import config
import random
import os
from bson.objectid import ObjectId


def parseArguments():
    parser = argparse.ArgumentParser(description='Fetch all urls from the pool')
    parser.add_argument('--pool', dest='pool', help='Pool id', required=True)
    parser.add_argument('--description', dest='description', help='Pool description', required=True)
    parser.add_argument('--rate', help='Sample rate', required=True, type=float)

    return parser.parse_args()


def fetchPool(argv):
    args = parseArguments()
    
    prev_poolId = ObjectId(args.pool)
    poolId = icoll.makePool(args.description)
    sys.stdout.write("Pool created with ID: %s\n" % poolId)
    
    pool_size = icoll.getPoolSize(args.pool)

    for index, row in enumerate(icoll.getPoolUrlsIterator(args.pool)):
        pool_info = [p for p in row['pools'] if p['poolId'] == prev_poolId][0]
        if random.random() < args.rate:
            icoll.assignToPool(row, poolId, pool_info['target'])
        progress_bar.printProgress(index + 1, pool_size)

    return


if __name__ == "__main__":
    fetchPool(sys.argv)
