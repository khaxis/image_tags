import os
from db_connector import *

def getDesctiption(nId):
    res = db.wordnet_words.find_one({'NId':nId})
    if res:
        return res['Description']
    return None


def findChildren(sourceNode, maxDepth=100):
    node = {'NId':sourceNode, 'children': list(), 'depth':0, 'description':getDesctiption(sourceNode)}
    res = node
    nodesToVisit = [node]
    while len(nodesToVisit) > 0:
        node = nodesToVisit[0]
        nodesToVisit = nodesToVisit[1:]
        if node['depth'] >= maxDepth:
            continue
        for row in db.wordnet_is_a.find({'NId':node['NId']}):
            newNode = {'NId':row['subNId'], 'children': list(), 'depth':node['depth']+1, 'description':getDesctiption(row['subNId'])}
            node['children'].append(newNode)
            nodesToVisit.append(newNode)
    return res


def findParents(sourceNode):
    res = []
    node = {'NId':sourceNode, 'description':getDesctiption(sourceNode)}
    nodesToVisit = [node]
    while True:
        res.append(node)
        parent = db.wordnet_is_a.find_one({'subNId':node['NId']})
        if parent is None:
            break
        node = {'NId':parent['NId'], 'description':getDesctiption(parent['NId'])}
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
