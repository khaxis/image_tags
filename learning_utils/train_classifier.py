#!/usr/bin/env python
import sys
import argparse
import pandas as pd
from utils import img_collection as icoll
from utils import progress_bar
from utils import config
from utils import progress_bar
import os
import uuid
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn import svm
from sklearn.metrics import accuracy_score, precision_score, confusion_matrix
from sklearn.externals import joblib


def parseArguments():
    parser = argparse.ArgumentParser(description='Train a classifier with a given pool')
    parser.add_argument('--pool-id', help='Pool id from the database', required=True)
    parser.add_argument('--nid', help='nID of the target column', required=True)
    parser.add_argument('--name', help='Name of the model')
    parser.add_argument('--include-test', help='Include test set into the learning pool while training', action='store_true')
    parser.add_argument('--slices', help='Space-separated list of slices', nargs='+', required=True)
    parser.add_argument('--description', help='Description of the trained model')


    return parser.parse_args()


def train_classifier_arg_parser(argv):
    args = parseArguments()

    poolId = args.pool_id
    nId = args.nid
    name = args.name
    include_test = args.include_test
    slices = args.slices
    description = args.description

    train_classifier(poolId, nId, name, include_test, slices, description)


def perf_measure(clf, X_test, y_test):
    CM = confusion_matrix(y_test, clf.predict(X_test))
    TN = CM[0][0]
    FN = CM[1][0]
    TP = CM[1][1]
    FP = CM[0][1]
    return(TP, FP, TN, FN)


def train_classifier(poolId, nId, name, include_test, slices, description):
    slices = sorted(slices)        # sort the list of slices just in case of misunderstanding in the future
    slices_set = set(slices)
    if not description:
        description = poolId + ' classification'
    assert type(nId) != None

    
    pd.set_option('display.expand_frame_repr', False)

    targets = []
    features = []
    for i, r in enumerate(icoll.getPoolUrlsIterator(poolId, include_test_set=include_test)):
        if 'slices' not in r:
            continue
        if not slices_set.issubset(r['slices']):
            continue
        targets.append([desc for desc in r['pools'] if str(desc['poolId']) == poolId][0]['target'])
        featureVector = []
        for sliceName in slices:
            featureVector += r['slices'][sliceName]['features']
        features.append(featureVector)

    X_train, X_test, y_train, y_test = train_test_split(features, targets, test_size=0.33)

    stats = []
    # Try to find best regularization parameters
    iter_values = range(0, 30)
    for i in range(len(iter_values)):
        C = 2 ** (iter_values[i] / 2.)
        clf = svm.SVC(kernel='rbf', C=C)
        accuracy = cross_val_score(clf, features, targets, cv=5, scoring='accuracy')
        f1 = cross_val_score(clf, features, targets, cv=5, scoring='f1')
        precision = cross_val_score(clf, features, targets, cv=5, scoring='precision')
        recall = cross_val_score(clf, features, targets, cv=5, scoring='recall')
        roc_auc = cross_val_score(clf, features, targets, cv=5, scoring='roc_auc')
        entry = {
            'model': 'SVC',
            'param': C,
            'accuracy': accuracy.mean(),
            'accuracy_interval90': accuracy.std()*2,
            'f1': f1.mean(),
            'precision': precision.mean(),
            'recall': recall.mean(),
            'roc_auc': roc_auc.mean()
        }
        #print '\t'.join([str(C)] + map(str, [v for k, v in entry.iteritems()]))
        stats.append(entry)
        progress_bar.printProgress(i + 1, len(iter_values))
    print

    stats = pd.DataFrame(stats)
    stats.sort_values(by=['f1', 'precision', 'roc_auc'], inplace=True, ascending=False)
    print stats

    C = stats.iloc[0]['param']
    estimated_score = dict(stats.iloc[0])

    print "Best regularization parameter so far: %f" % C
    clf = svm.SVC(kernel='rbf', C=C).fit(features, targets)
    workingDir = config.getDataPath()
    storePath = os.path.join(workingDir, 'data', 'models')
    destination = os.path.join(storePath, str(uuid.uuid1()) + '.pkl')
    
    joblib.dump(clf, destination, compress=3)
    icoll.makeClassificationModel(
        pool_id=poolId,
        description=description,
        nId=nId,
        slices=slices,
        estimated_score=estimated_score,
        path=destination,
        include_test_set=include_test
        )


if __name__ == "__main__":
    train_classifier_arg_parser(sys.argv)
