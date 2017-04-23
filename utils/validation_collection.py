import datetime
import dateutil.parser
from utils.db_connector import db
from utils.common import toObjectID


def insertValidationImage(path, src_id, src_modified_time):
    return db.validation_image.insert(
        {
            'path': path,
            'date_inserted': datetime.datetime.utcnow(),
            'src_id': src_id,
            'src_modified_time': dateutil.parser.parse(src_modified_time)
        })

def findBySrcId(src_id):
    return db.validation_image.find_one({
            'src_id': src_id
        })