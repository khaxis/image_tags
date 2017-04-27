#!/usr/bin/env python
import sys
import argparse
from learning_utils.predictor import Predictor
from utils import validation_collection as vcoll
from utils import progress_bar


def parseArguments():
    parser = argparse.ArgumentParser(description='Apply a model result to validation set')
    parser.add_argument('-m', '--model-id', help='Model id from the database', required=True)
    parser.add_argument('--test-mode', help='Do nothing', action='store_true')
    return parser.parse_args()


def fetch_validation(argv):
    args = parseArguments()

    if args.test_mode:
        print("TEST MODE")

    predictor = Predictor(args.model_id)

    i = 0
    totalCount = vcoll.getSize()
    with vcoll.getImageIterator() as cursor:
        cursor.batch_size(100)
        for row in cursor:
            if 'slices' in row:
                prediction = predictor.predict_on_slices(row['slices'])[0]
                vcoll.updatePrediction(row, args.model_id, prediction)
            i += 1
            progress_bar.printProgress(i, totalCount)

        print()

if __name__ == "__main__":
    fetch_validation(sys.argv)
