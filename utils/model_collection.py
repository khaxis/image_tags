import os
import datetime
from utils.db_connector import db
from utils.common import toObjectID


def getModelsList(pool_id=None):
    fltr = {}
    if pool_id:
        fltr = {'pool_id': toObjectID(pool_id)}
    res = db.classification_model.find(fltr).sort('date_inserted', -1)
    return res

def getModel(model_id):
    model_id = toObjectID(model_id)
    res = db.classification_model.find_one({'_id': model_id})
    return res

def getModelsByPoolId(pool_id):
    pool_id = toObjectID(pool_id)
    res = db.classification_model.find({'pool_id': pool_id})
    return res

def makeClassificationModel(pool_id, description, nId, slices, estimated_score, path, include_test_set):
    return db.classification_model.insert(
        {
            'description': description,
            'date_inserted': datetime.datetime.utcnow(),
            'nId': nId,
            'deprecated': False,
            'slices': slices,
            'estimated_score': estimated_score,
            'path': path,
            'include_test_set': include_test_set,
            'pool_id': toObjectID(pool_id)
        })
