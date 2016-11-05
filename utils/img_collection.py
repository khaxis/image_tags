import os
import datetime
from db_connector import *
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
    print '%s-%s: %s'%(' '*depth*4, tree['NId'], tree['description'])
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


def makePool(description):
    return db.pool.insert({'description':description, 'date_inserted':datetime.datetime.utcnow()})


def assignToPool(urlRecord, poolId, target):
    db.image_urls.update_one(
        {'_id':urlRecord['_id']},
        {'$push':
            {
            'pools':
                {
                'poolId': poolId,
                'target':target
                }
            }
        }
    )


def getPoolUrlsIterator(poolId):
    if type(poolId) == str:
        poolId = ObjectId(poolId)
    return db.image_urls.find({'pools.poolId':poolId})


def getPoolSize(poolId, downloadedOnly=False):
    if type(poolId) == str:
        poolId = ObjectId(poolId)
    query = {'pools.poolId':poolId}
    if downloadedOnly:
        query['downloadable'] = True
    return db.image_urls.count(query)


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
