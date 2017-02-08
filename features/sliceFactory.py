#!/usr/bin/env python
from features.bowSift100.BOWSift100 import BOWSift100

featuresSet = {BOWSift100()}

def getExtractors():
    return featuresSet
