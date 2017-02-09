from utils import model_collection as mcoll
from features import sliceFactory
from sklearn.externals import joblib
import numpy as np

class Predictor():
    """Loads a model and slices. Should predict a target value by an input like an image.
    The class should take care of slices and models initialization."""

    def __init__(self, model_id):
        self.model_description = mcoll.getModel(model_id)
        self.slices = sorted(self.model_description['slices'])
        path = self.model_description['path']
        self.model = joblib.load(path)
        self.extractors = sliceFactory.getParticularExtractorsDict(self.slices)


    def predict(self, images):
        if type(images) is not list:    # make sure it works correctly with both images and lists of images
            images = [images]

        res = []
        for im in images:
            if im is None:
                res.append(None)
                continue

            featureVector = np.array([])
            for sliceName in self.slices:
                p = self.extractors[sliceName].extract(im)
                featureVector = np.concatenate([featureVector, self.extractors[sliceName].extract(im)[0]], axis=0)
            res.append(featureVector)

        return self.model.predict(np.stack(res, axis=0))