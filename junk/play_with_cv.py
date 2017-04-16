import sys
import os
from utils import img_collection as icoll
import cv2
import numpy as np
from sklearn.externals import joblib
from scipy.cluster.vq import *
from sklearn.preprocessing import StandardScaler
from boto import storage_uri
import io


def get_image(image_path, cv2_img_flag=0):
    root = 'gs://image_tags/images/'
    content = storage_uri(root + image_path)
    img_stream = io.BytesIO()
    content.get_contents_to_file(img_stream)
    img_stream.seek(0)
    img_array = np.asarray(bytearray(img_stream.read()), dtype=np.uint8)
    return cv2.imdecode(img_array, cv2_img_flag)

def train():

    trainPool = []

    for i, r in enumerate(icoll.getPoolUrlsIterator('581e06de0310e9180b1f7a62')):
        if r['valid_image']:
            trainPool.append(r)
        if i>10:
            break

    # Create feature extraction and keypoint detector objects
    fea_det = cv2.xfeatures2d.SIFT_create() #cv2.FeatureDetector_create("SIFT")
    des_ext = fea_det # cv2.DescriptorExtractor_create("SIFT")

    # List where all the descriptors are stored
    des_list = []

    for imageRow in trainPool:
        #im = cv2.imread(imageRow['path'])
        im = get_image(imageRow['IId'])
        if im is None:
            continue
        kpts = fea_det.detect(im)
        kpts, des = des_ext.compute(im, kpts)
        des_list.append(des)


    # Stack all the descriptors vertically in a numpy array
    descriptors = des_list[0][1]
    for descriptor in des_list[1:]:
        descriptors = np.vstack((descriptors, descriptor))

    # Perform k-means clustering
    k = 100
    voc, variance = kmeans(descriptors, k, 1)


    words, distance = vq(des_list[0],voc)


    ##
    imFeatures = np.zeros((len(des_list), k), "float32")
    for i in range(len(des_list)):
        words, distance = vq(des_list[i],voc)
        for w in words:
            imFeatures[i][w] += 1

    # Scaling the words
    stdSlr = StandardScaler().fit(imFeatures)
    joblib.dump((stdSlr, k, voc), "SIFT_bow_k100.pkl", compress=3)
    #imFeatures = stdSlr.transform(imFeatures)


if __name__ == '__main__':
    train()
