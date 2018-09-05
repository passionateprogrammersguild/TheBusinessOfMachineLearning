import sys, os, time
import numpy as np
from loggers import *
from common import FeatureMap, FactorMap, Model

def create(modeldir, logger=StdOutLogger):
        start = time.time()
        featuremap           = FeatureMap.parse(modeldir)
        factormap            = FactorMap.parse(modeldir)
        binarymodel          = Model.deserialize(modeldir)
                    
        model = PlayRunRatioModel(binarymodel, featuremap, factormap)

        model.logger.info("Elapsed time to create model {0}".format((time.time() - start)))
        return model

class InvalidFeatureException(Exception):
   
    def __init__(self, messages):
        Exception.__init__(self)
        self.messages = messages
        
    def to_dict(self):
        rv = {}
        rv['messages'] = self.messages
        return rv

class PlayRunRatioModel:
    def __init__(self, model, featuremap, factormap, logger = None):
         self.model = model
         self.featuremap = featuremap
         self.factormap = factormap
         self.logger = logger if logger is not None else StdOutLogger    

    def verifyexample(self, example):
        if example == None:
            raise InvalidFeatureException(['example cannot be null'])

        badfactorlevelvalues = []
        
        #TODO:  write warnings and mean replace missing values

        #verify the categorical features have valid values
        for featurename, featurevalue in example.items():
            if featurename not in self.featuremap:                
                self.logger.error("invalid feature " + featurename)
                badfactorlevelvalues.append("invalid feature " + featurename)

            if featurename in self.factormap:

                if featurevalue not in self.factormap[featurename]:
                    validvalues = ','.join(self.factormap[featurename].keys())
                    badfactorlevelvalues.append("invalid value of {0} for feature {1}.  Valid values are {2}".format(featurevalue, featurename, validvalues))
    
        if len(badfactorlevelvalues) > 0:
            raise InvalidFeatureException(badfactorlevelvalues)

    def predict(self, example, debug=False):
        def isnumber(value):
            try:
                float(value)
                return True
            except Exception:
                return False
        
        def transformxfeature(featurename, featurevalue, factormap):
                        
            if (featurename in factormap and str(featurevalue) in factormap[featurename]):
                return factormap[featurename][str(featurevalue)]

            if (isnumber(featurevalue)):
                return featurevalue
            
            self.logger.error("feature name {0} feature value: {0}".format(featurename, featurevalue))
            raise InvalidFeatureException(["invalid feature {0}".format(featurename)])

        self.verifyexample(example)
        
        #initialize variables
        numfeatures = len(self.featuremap)
        
        #initilize the matricies for prediction
        featurematrix = np.zeros((1, numfeatures), dtype=float)        
        
        #build up the feature matrix based on the properties of the example and the featuremap
        for featurename, featurevalue in example.items():
            if featurename in self.featuremap:
                xpos = self.featuremap[featurename]
                xval = transformxfeature(featurename, featurevalue, self.factormap)
                
                if xval is not None:
                    if debug:
                        self.logger.info("xpos {0} name {1} val {2} featureval {3}".format(xpos, featurename, featurevalue, xval))
                    
                    featurematrix[0][int(xpos)-1] = xval

        self.logger.info("featurematrix.shape {0}".format(featurematrix.shape))
        self.logger.info("feature matrix {0}".format(featurematrix))

        pred = self.model.predict(featurematrix)[0]
        self.logger.debug("prediction {0} on example {1}".format(pred, example))
        return pred

# We only need this for local development.
if __name__ == '__main__':
    modeldir = sys.argv[1] #path to model directory

    model = create(modeldir)

    #create an example to predict the run/pass ratio
    example = {
        'Drive': 17,
        'qtr': 3,
        'down': 2,
        'ydstogo': 18,
        'SideofField': 'PosTeam',
        'PosTeam': 'HomeTeam',
        'YdsToTD': 68,
        'TimeLeftInQtr':8.31,
        'PercentageOfField':.4
    }
        
    #build up a string for the features and values in the example
    features = '\n'.join(['{0}:{1}'.format(k,v) for (k,v) in example.items()])

    print("\nfeatures: \n{0} \nPredicted Run Pass Ratio: {1}".format(features, model.predict(example)))