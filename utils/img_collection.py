import os
import datetime
from utils.db_connector import *
from bson.objectid import ObjectId

def getDesctiption(nId):
    res = db.wordnet_words.find_one({'NId':nId})
    if res:
        return res['Description']
    return None


def findChildren(sourceNode, maxDepth=100, excludeNIds = None):
    node = {'NId':sourceNode, 'children': list(), 'depth':0, 'description':getDesctiption(sourceNode)}
    res = node
    nodesToVisit = [node]
    if excludeNIds is not None:
        excludeNIds = set(excludeNIds)
    else:
        excludeNIds = set()

    while len(nodesToVisit) > 0:
        node = nodesToVisit[0]
        nodesToVisit = nodesToVisit[1:]
        if node['depth'] >= maxDepth:
            continue
        for row in db.wordnet_is_a.find({'NId':node['NId']}):
            if row['subNId'] in excludeNIds:
                continue
            newNode = {'NId':row['subNId'], 'children': list(), 'depth':node['depth']+1, 'description':getDesctiption(row['subNId'])}
            node['children'].append(newNode)
            nodesToVisit.append(newNode)
    return res


def findParents(sourceNode):
    res = []
    node = {'NId':sourceNode, 'description':getDesctiption(sourceNode)}
    nodesToVisit = [node]
    while True:
        parent = db.wordnet_is_a.find_one({'subNId':node['NId']})
        if parent is None:
            break
        node = {'NId':parent['NId'], 'description':getDesctiption(parent['NId'])}
        res.append(node)
    return res


def printTree(tree, depth=0):
    print('%s-%s: %s'%(' '*depth*4, tree['NId'], tree['description']))
    for child in tree['children']:
        printTree(child, depth+1)


def getNIdsRecursive(treeNode, res):
    res.append(treeNode['NId'])
    for child in treeNode['children']:
        getNIdsRecursive(child, res)


def getTreeUrls(tree):
    res = []
    nIds = []
    getNIdsRecursive(tree, nIds)
    for row in db.image_urls_collection.find({'$or': [{'NId':nid} for nid in nIds]}):
        res.append(row['Urls'])
    
    return res

def getFlattenUrlsTree(tree):
    res = []
    nIds = []
    getNIdsRecursive(tree, nIds)
    for row in db.image_urls.find({'$or': [{'NId':nid} for nid in nIds]}):
        res.append(row)
    return res


def _findRandomDocuments(collection, randomDocumentsCount):
    randomDocumentsRatio = float(randomDocumentsCount) / collection.count()
    return collection.find({'$where':"function () {return Math.random()<%f}" % randomDocumentsRatio})


def findRandomImageUrlsDocuments(randomDocumentsCount):
    res = []
    for row in _findRandomDocuments(db.image_urls, randomDocumentsCount):
        res.append(row)
    return res


def assignToPool(urlRecord, poolId, target, in_train_set=True):
    db.image_urls.update_one(
        {'_id':urlRecord['_id']},
        {'$push':
            {
            'pools':
                {
                'poolId': poolId,
                'target':target,
                'in_train_set': in_train_set
                }
            }
        }
    )


def getPoolUrlsIterator(poolId, include_train_set=True, include_test_set=True):
    if type(poolId) != ObjectId:
        poolId = ObjectId(poolId)
    if not include_train_set and not include_test_set:
        return None
    elif include_train_set and include_test_set:
        return db.image_urls.find({'pools.poolId':poolId})
    return db.image_urls.find(
        {'$and': [
            {'pools.poolId': poolId}, 
            {'$or': [
                {"pools.in_train_set": {'$exists': False}},
                {"pools.in_train_set": include_train_set}    # eigher include_train_set or include_test_set is set to True, not both
                ]}
            ]
        },
        no_cursor_timeout=True)


def updateImagePath(imageRecord, path):
    return db.image_urls.update_one(
        {'_id':imageRecord['_id']},
        {
        '$set':
            {
            'path':path
            }
        }
    )

def updateImageDownloadableStatus(imageRecord, downloadable):
    return db.image_urls.update_one(
        {'_id':imageRecord['_id']},
        {
        '$set':
            {
            'downloadable':downloadable
            }
        }
    )

def updateImageValidStatus(imageRecord, valid_image):
    return db.image_urls.update_one(
        {'_id':imageRecord['_id']},
        {
        '$set':
            {
            'valid_image':valid_image
            }
        }
    )

def updateImageSlices(imageRecord, slices):
    return db.image_urls.update_one(
        {'_id':imageRecord['_id']},
        {
        '$set':
            {
            'slices':slices
            }
        }
    )

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
            'pool_id': ObjectId(pool_id)
        })
