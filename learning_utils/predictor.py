from utils import model_collection as mcoll
from utils.file_handler import get_file_stream
from features import sliceFactory
from sklearn.externals import joblib
import numpy as np
import tempfile


class Predictor():
    """Loads a model and slices. Should predict a target value by an input like an image.
    The class should take care of slices and models initialization."""

    def __init__(self, model_id):
        self.model_description = mcoll.getModel(model_id)
        self.slices = sorted(self.model_description['slices'], key=lambda x: (x['name'], x['version']))

        # handle the model file
        path = self.model_description['path']
        tmp_filename = tempfile.mktemp()
        with open(tmp_filename, 'wb') as fp:
            fp.write(get_file_stream(path).getvalue())
        self.model = joblib.load(tmp_filename)

        self.extractors = sliceFactory.getParticularExtractorsDict([slice_obj['name'] for slice_obj in self.slices])


    def predict(self, images):
        if type(images) is not list:    # make sure it works correctly with both images and lists of images
            images = [images]

        res = []
        for im in images:
            if im is None:
                res.append(None)
                continue

            featureVector = np.array([])
            for slice_obj in self.slices:
                slice_name = slice_obj['name']
                p = self.extractors[slice_name].extract(im)
                featureVector = np.concatenate([featureVector, self.extractors[slice_name].extract(im)[0]], axis=0)
            res.append(featureVector)

        return self.model.predict(np.stack(res, axis=0))


    def predict_on_slices(self, records):
        """records is a list or a single instanse of an object with 'slices' field Slices object.
        i.e. Slices is a list [{'name':'BOW', 'features': [1, 0, 1]}, ...]
        """
        if type(records) is not list:    # make sure it works correctly with both images and lists of images
            records = [records]

        res = []
        for row in records:
            if row is None:
                res.append(None)
                continue

            featureVector = np.array([])
            for slice_obj in self.slices:
                slice_name = slice_obj['name']
                features = np.array(row[slice_name]['features'])
                featureVector = np.concatenate([featureVector, features], axis=0)
            res.append(featureVector)

        return self.model.predict(np.stack(res, axis=0))
