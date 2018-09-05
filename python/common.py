import os, pickle, traceback
from sklearn.preprocessing import LabelEncoder

class Model:
    @staticmethod
    def serialize(obj, path):
        with open(os.path.join(path, "MODEL.pckl"), 'wb') as f:
            pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def deserialize(path):
        with open(os.path.join(path, "MODEL.pckl"), 'rb') as f:
            return pickle.load(f)

class FeatureMap:
    
    @staticmethod
    def parse(path, invert=False):

        featuremap = {}
        # example input ...
        # 1:2d;2:2d development;3:2d modeling;4:3d;5:3d cad;6:3d data;
        with open(os.path.join(path, "FEATUREMAP"), 'r') as featuremapfile:
            content = featuremapfile.read()

            for pairs in content.split(';'):
                if (len(pairs) > 0):
                    index_name = pairs.split(':')
                    index = index_name[0]
                    name = index_name[1]

                    if invert == False:
                        featuremap[name] = index
                    else:
                        featuremap[index] = name
        
        return featuremap

    @staticmethod
    def save(features, path):
        assert isinstance(features, list), "Only list is supported"

        with open(os.path.join(path, "FEATUREMAP"), "w") as fp:
            for i, k in enumerate(features):
                fp.write(str(i+1)+":"+k+";")

class FactorMap:
    @staticmethod
    def parse(path):        

        factormap = {}
        
        with open(os.path.join(path, "FACTORMAP"), 'r') as factormapfile:
            content = factormapfile.read()
            
            # example row ...
            # BF_REQUEST_TYPE:Job Requisition^0.0|Named Request^1.0|SOW^2.0|Worker Tracking^3.0;BF_TOTAL_CONTRACT_LENGTH:1 to 2 years^0.0|181 to 270 days^1.0|2 to 3 years^2.0|271 to 365 days^3.0|31 to 90 days^4.0|7 to 30 days^5.0|91 to 180 days^6.0|< 7 days^7.0|> 3 years^8.0;
            for row in content.split(';'):
                
                factorname, factorvalues = row.split(':')                
                
                factormap[factorname] = {}
                for feature in factorvalues.split('|'):

                    name, index = feature.split('^')

                    factormap[factorname][name] = index

        return factormap

    @staticmethod
    def save(lemap, path):
        assert isinstance(lemap, dict), "Only dict is supported"
        assert len(lemap) > 0, "Do not support empty dictionaries"

        keys = list(lemap.keys())
        assert isinstance(lemap[keys[0]], LabelEncoder), "Only LabelEncoder is supported but got " + type(lemap[keys[0]])

        # example output ...
        # STANDARDIZED_JOB_LEVEL:Entry^0.0|Undefined^4.0|Mid^2.0|Senior^3.0|Expert/Specialized^1.0;
        with open(os.path.join(path, "FACTORMAP"), "w") as fp:
            lineno = 0
            for factorname, le in lemap.items():
                if lineno > 0:
                    fp.write(';')

                fp.write(factorname + ':')

                #print the factornames / classes_
                classes = list(le.classes_)
                values = None

                try:
                    values  = le.transform(classes)
                except:
                    exc_type, exc_value, tb = sys.exc_info()
                    raise ValueError("error creating factor levels for " + factorname + " because " + '\n'.join(traceback.format_exception_only(exc_type, exc_value)))
                

                assert len(classes) == len(values)

                fp.write('|'.join([str(classes[i]) + "^" + str(float(values[i])) for i,x in enumerate(classes)]))
                lineno +=1