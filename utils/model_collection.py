import os
import datetime
from db_connector import *
from bson.objectid import ObjectId


def getModelsList():
	res = db.classification_model.find().sort('date_inserted', -1)
	return res


def getPool(poolId):
	if type(poolId) != ObjectId:
		poolId = ObjectId(poolId)
	res = db.pool.find({'_id': poolId}).limit(1)
	return res
