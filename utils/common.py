from bson.objectid import ObjectId

def toObjectID(_id):
	if type(_id) != ObjectId:
		_id = ObjectId(_id)
	return _id