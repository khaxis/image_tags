import os
import datetime
from utils.db_connector import *
from bson.objectid import ObjectId
from utils.common import toObjectID


def makePool(description):
    return db.pool.insert({'description':description, 'date_inserted':datetime.datetime.utcnow()})


def getPoolsList():
    res = db.pool.find().sort('date_inserted', -1)
    return res


def getPool(poolId):
    poolId = toObjectID(poolId)
    res = db.pool.find({'_id': poolId}).limit(1)
    return res


def getSampleOfImages(poolId, sample_size=None):
    poolId = toObjectID(poolId)
    if sample_size is None:
        return db.image_urls.find(
                    {'pools.poolId': poolId}
                )
    else:
        return db.image_urls.find(
                    {'pools.poolId': poolId}
                ).limit(sample_size)


def getPoolSize(poolId, downloaded_only=False, valid_only=False):
    if type(poolId) != ObjectId:
        poolId = ObjectId(poolId)
    query = {'pools.poolId':poolId}
    if downloaded_only:
        query['downloadable'] = True
    if valid_only:
        query['valid_image'] = True
    return db.image_urls.count(query)
