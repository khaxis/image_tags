import os
import datetime
from db_connector import *
from bson.objectid import ObjectId
from common import toObjectID


def getPoolsList():
	res = db.pool.find().sort('date_inserted', -1)
	return res


def getPool(poolId):
	poolId = toObjectID(poolId)
	res = db.pool.find({'_id': poolId}).limit(1)
	return res


def getSampleOfImages(poolId, sample_size=None):
	poolId =toObjectID(poolId)
	if sample_size is None:
		return db.image_urls.find(
					{'pools.poolId': poolId}
				)
	else:
		return db.image_urls.find(
					{'pools.poolId': poolId}
				).limit(sample_size)