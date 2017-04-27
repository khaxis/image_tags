#!/usr/bin/env python
import sys
import argparse
import cv2
from utils import validation_collection as vcoll
from utils import progress_bar
from utils import image_handler
from features import sliceFactory


def parseArguments():
    parser = argparse.ArgumentParser(description='Recalculate slices in necessary')
    parser.add_argument('--test-mode', help='Do nothing, but return prepared pool', action='store_true')
    return parser.parse_args()

def fetch_validation(argv):
    args = parseArguments()

    if args.test_mode:
        print("TEST MODE")

    i = 0
    totalCount = vcoll.getSize()
    extractors = sliceFactory.getExtractors()
    with vcoll.getImageIterator() as cursor:
        cursor.batch_size(100)
        for row in cursor:
            im = None
            slices = {}
            for extractor in extractors:
                extractor_name = extractor.getName()
                if 'slices' in row and extractor_name in row['slices'] and row['slices'][extractor_name]['version'] == extractor.getVersion():
                    continue # no need to go on if features already extracted with the current version
                if im is None:
                    im = image_handler.get_image(row['path'])
                    ratio = max(500. / im.shape[0], 500. / im.shape[1])
                    im = cv2.resize(im, (0,0), fx=ratio, fy=ratio)
                features = extractor.extract(im)
                if features[0] is not None:
                    entry = {}
                    entry['features'] = features[0].tolist()
                    entry['version'] = extractor.getVersion()
                    slices[extractor_name] = entry

            if len(slices) > 0:
                vcoll.updateSlices(row, slices)

            i += 1
            progress_bar.printProgress(i, totalCount)

        print()


if __name__ == "__main__":
    fetch_validation(sys.argv)
