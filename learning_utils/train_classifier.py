#!/usr/bin/env python
import sys
import argparse
import pandas as pd
from utils import img_collection as icoll
from utils import progress_bar

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn import svm
from sklearn.metrics import accuracy_score, precision_score, confusion_matrix


def parseArguments():
	parser = argparse.ArgumentParser(description='Train a classifier with a given pool')
	parser.add_argument('--pool-id', help='Pool id from the database', required=True)
	parser.add_argument('--nid', help='nID of the target column')
	parser.add_argument('--name', help='Name of the model')
	parser.add_argument('--include-test', help='Include test set into the learning pool while training', action='store_true')
	parser.add_argument('--slices', help='Space-separated list of slices', nargs='+', required=True)

	return parser.parse_args()


def train_classifier_arg_parser(argv):
	args = parseArguments()

	poolId = args.pool_id
	nId = args.nid
	name = args.name
	include_test = args.include_test
	slices = args.slices

	train_classifier(poolId, nId, name, include_test, slices)


def perf_measure(clf, X_test, y_test):
    CM = confusion_matrix(y_test, clf.predict(X_test))
    TN = CM[0][0]
    FN = CM[1][0]
    TP = CM[1][1]
    FP = CM[0][1]
    return(TP, FP, TN, FN)


def train_classifier(poolId, nId, name, include_test, slices):
	slices = sorted(slices)		# sort the list of slices just in case of misunderstanding in the future
	slices_set = set(slices)
	
	pd.set_option('display.expand_frame_repr', False)

	targets = []
	features = []
	for i, r in enumerate(icoll.getPoolUrlsIterator(poolId)):
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
	for i in range(0,15):
		C = 2**(i/10.)
		clf = svm.SVC(kernel='rbf', C=C).fit(X_train, y_train)
		y_hat = clf.predict(X_test)
		score = clf.score(X_test, y_test)
		scores = cross_val_score(clf, X_test, y_test, cv=5)
		print scores
		precision = precision_score(y_hat, y_test)
		TP, FP, TN, FN = perf_measure(clf, X_train, y_train)
		print '\t'.join(map(str, [C, score, precision, TP, FP, TN, FN]))
		entry = {
			'model': 'SVC',
			'param': C,
			'score': score, 
			'score_mean': scores.mean(),
			'score_interval90': scores.std()*2,
			'precision': precision, 
			'TP': TP, 
			'FP': FP, 
			'TN': TN, 
			'FN': FN
		}
		stats.append(entry)

	stats = pd.DataFrame(stats)
	stats.sort_values(by=['score', 'precision'], inplace=True, ascending=False)
	print stats
	print stats.iloc[0]['param']




if __name__ == "__main__":
	train_classifier_arg_parser(sys.argv)
