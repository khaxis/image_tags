#!/usr/bin/env python
import sys
import argparse
from utils import img_collection as icoll
from utils import pool_collection as pcoll
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
    parser.add_argument('-o', '--out', help='Store resulting pool in out')
    parser.add_argument('--test-mode', help='Do nothing, but return prepared pool', action='store_true')

    return parser.parse_args()


def fetchPool(argv):
    args = parseArguments()
    
    if args.test_mode:
        if args.out:
            with open(args.out, 'w') as f:
                f.write(args.pool)
        return

    prev_poolId = ObjectId(args.pool)
    poolId = pcoll.makePool(args.description)
    sys.stdout.write("Pool created with ID: %s\n" % poolId)
    
    pool_size = pcoll.getPoolSize(args.pool)

    for index, row in enumerate(icoll.getPoolUrlsIterator(args.pool)):
        pool_info = [p for p in row['pools'] if p['poolId'] == prev_poolId][0]
        if random.random() < args.rate:
            icoll.assignToPool(row, poolId, pool_info['target'])
        progress_bar.printProgress(index + 1, pool_size)

    if args.out:
        with open(args.out, 'w') as f:
            f.write(str(poolId))

    return


if __name__ == "__main__":
    fetchPool(sys.argv)
