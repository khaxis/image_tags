import os
import datetime
from db_connector import *
from common import toObjectID


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
