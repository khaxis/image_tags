#!/usr/bin/env python
from features.bowSift100.bowSift100 import BOWSift100

featuresSet = {BOWSift100()}

def getExtractors():
    return featuresSet

def getParticularExtractorsDict(extractor_names):
    return {
        extractor.getName(): extractor
            for extractor in getExtractors() if extractor.getName() in extractor_names
    }

