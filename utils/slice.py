import sys
from db_connector import *
from bson.objectid import ObjectId

def getSlice(name):
    res = db.slice.find_one({'name':name})
    if res is None:
        raise Exception("Slice '%s' is not found" % name)
    return res
