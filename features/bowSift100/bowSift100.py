#!/usr/bin/env python
from features.baseSlice.baseSlice import BaseSlice
from utils import img_collection as icoll
import cv2
import numpy as np
from sklearn.externals import joblib
from scipy.cluster.vq import *
from sklearn.preprocessing import StandardScaler
import utils.slice


class BOWSift100(BaseSlice):
    __stdSlr = None
    __k = None
    __voc = None
    __initiated = False

    def __init__(self, modelFilename=None):
        if modelFilename:
            self.loadModel(modelFilename)
        else:
            sliceDescriptor = utils.slice.getSlice(self.getName())
            self.loadModel(sliceDescriptor['model_path'])

        # Create feature extraction and keypoint detector objects
        self.__fea_det = cv2.FeatureDetector_create("SIFT")
        self.__des_ext = cv2.DescriptorExtractor_create("SIFT")


    def getVersion(self):
        """Get a version number as int"""
        return 0


    def extract(self, images):
        """
        Extract features of the given images
        Note: modelFilename must be provided. Otherwise will return None
        """
        if not self.__initiated:
            return None
        if type(images) is not list:    # make sure it works correctly with both images and lists of images
            images = [images]

        res = []
        for im in images:
            if im is None:
                res.append(None)
                continue
            kpts = self.__fea_det.detect(im)
            if len(kpts) == 0:  # no key points detected
                res.append(None)
                continue
            kpts, des = self.__des_ext.compute(im, kpts)
            imFeatures = np.zeros((1, self.__k), "float32")
            words, distance = vq(des, self.__voc)
            for w in words:
                imFeatures[0][w] += 1
            imFeatures = self.__stdSlr.transform(imFeatures)
            res.append(imFeatures[0])

        return np.stack(res, axis=0)


    def getName(self):
        """Get name of the slice"""
        return 'bowSift100'


    def loadModel(self, modelFilename):
        self.__stdSlr, self.__k, self.__voc = joblib.load(modelFilename)
        self.__initiated = True

if __name__ == "__main__":
    print("BOWSift100")

