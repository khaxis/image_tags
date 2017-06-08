#!/usr/bin/env python
import sys
import argparse
from utils import img_collection as icoll
from utils import pool_collection as pcoll
from utils import web_utils
from utils import progress_bar
from utils import config
from utils import file_handler
from utils import image_handler
from features import sliceFactory
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

def parseArguments():
    parser = argparse.ArgumentParser(description='Fetch all urls from the pool')
    parser.add_argument('--pool', dest='pool', help='Pool id', required=True)
    parser.add_argument('--test-mode', help='Do nothing, but return prepared pool', action='store_true')
    parser.add_argument('--threads-number', help='The number of concurent threads', type=int, default=10)
    parser.add_argument('--ignore-caching', help='Skip downloading images step', action='store_false')

    return parser.parse_args()


def downloadAndUpdateImage(storePath, row):
    if 'path' not in row:
        destination = os.path.join(storePath, row['IId'])
        file_content = web_utils.get_file_stream(row['Url'])
        if file_content and image_handler.is_valid_image(file_content):
            try:
                file_handler.upload_file_stream(destination, file_content)
            except:
                pass
            # the image successfully saved
            icoll.updateImagePath(row, destination)
            icoll.updateImageDownloadableStatus(row, True)
            icoll.updateImageValidStatus(row, True)
        else:
            icoll.updateImageDownloadableStatus(row, False)
            icoll.updateImageValidStatus(row, False)
    else:
        # temporary
        file_path = row['path']
        if file_path.startswith('/Users'):
            file_path = 'image_tags/images/' + row['IId']
            icoll.updateImagePath(row, file_path)
        file_content = file_handler.get_file_stream(file_path)
        valid_status = image_handler.is_valid_image(file_content)
        icoll.updateImageValidStatus(row, valid_status)


def fetchPool(argv):
    args = parseArguments()

    if args.test_mode:
        print("TEST MODE")
        return
    
    workingDir = config.getDataPath()
    storePath = os.path.join(workingDir, 'images')

    totalCount = pcoll.getPoolSize(args.pool)
    if args.ignore_caching:
        i = 0
        futures = []
        with ThreadPoolExecutor(max_workers=args.threads_number) as executor:
            with icoll.getPoolUrlsIterator(args.pool) as cursor:
                cursor.batch_size(100)
                for row in cursor:
                    future = executor.submit(downloadAndUpdateImage, storePath, row)
                    futures.append(future)
                print()

            print("Executors scheduled")
            for f in as_completed(futures):
                i += 1
                progress_bar.printProgress(i, totalCount)
            print()
        print("Pool cached")
    else:
        print("Ignoring pool caching")
    print("Extracting features...")

    i = 0
    extractors = sliceFactory.getExtractors()
    with icoll.getPoolUrlsIterator(args.pool) as cursor:
        cursor.batch_size(100)
        for row in cursor:
            if row['valid_image']:
                im = None
                slices = {}
                for extractor in extractors:
                    extractor_name = extractor.getName()
                    if 'slices' in row and extractor_name in row['slices'] and row['slices'][extractor_name]['version'] == extractor.getVersion():
                        continue # no need to go on if features already extracted with the current version
                    if im is None:
                        im = image_handler.get_image(row['path'])
                    features = extractor.extract(im)
                    if features[0] is not None:
                        entry = {}
                        entry['features'] = features[0].tolist()
                        entry['version'] = extractor.getVersion()
                        slices[extractor_name] = entry

                if len(slices) > 0:
                    icoll.updateImageSlices(row, slices)

            i += 1
            progress_bar.printProgress(i, totalCount)
        print()

    return


if __name__ == "__main__":
    fetchPool(sys.argv)
