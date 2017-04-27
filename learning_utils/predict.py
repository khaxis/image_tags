#!/usr/bin/env python
import sys
import argparse
from learning_utils.predictor import Predictor
import cv2

def parseArguments():
    parser = argparse.ArgumentParser(description="Predict target values given images and a model."
                                                 "Note stdin is input and is in tsv format. First column is the path"
                                                 "to the image. in output the first column will be replaced with the value"
                                                 "of predicted target. The rest columns will remain unchanged.")
    parser.add_argument('-m', '--model-id', help='Model id from the database', required=True)

    return parser.parse_args()


def predict(argv):
    args = parseArguments()
    predictor = Predictor(args.model_id)

    ims = []
    for line in sys.stdin:
        splitted_line = line.strip().split('\t')
        if len(splitted_line) == 0:
            continue
        path = splitted_line[0]
        im = cv2.imread(path)
        ratio = max(500. / im.shape[0], 500. / im.shape[1])
        im = cv2.resize(im, (0,0), fx=ratio, fy=ratio)
        splitted_line[0] = str(predictor.predict(im)[0]) 
        print('\t'.join(splitted_line))


if __name__ == "__main__":
    predict(sys.argv)
