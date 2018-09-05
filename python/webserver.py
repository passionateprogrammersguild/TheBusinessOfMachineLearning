import os
import numpy as np

from flask import Flask
from flask import jsonify
from flask import request
from flask import abort
from flask import make_response

from playrunratiomodel import create, InvalidFeatureException

app = Flask(__name__)
regression = create(os.path.join("./model/", "regression"))
classification = create(os.path.join("./model/", "multiclassclassification"))
binaryclassification = create(os.path.join("./model/", "binaryclassification"))

def predict(model, example):
    
    model.verifyexample(example)
    result = model.predict(example)
    print("have result",result,"of type",type(result))
    if type(result) == np.int64:
       print("INFO: converting np.int64",result,"to an int")
       return int(result)
    
    return result

@app.route("/regression",  methods=['POST'])
def runpassratio():
    if not request.json:
        abort(400)

    return make_response(jsonify({'runpassratio': predict(regression, request.json)}), 200)

@app.route("/multiclassclassification",  methods=['POST'])
def runpass():
    if not request.json:
        abort(400)

    return make_response(jsonify({'runpass': predict(classification, request.json)}), 200)

@app.route("/binaryclassification",  methods=['POST'])
def isrunpass():
    if not request.json:
        abort(400)
    
    return make_response(jsonify({'isrun': predict(binaryclassification, request.json)}), 200)


@app.errorhandler(InvalidFeatureException)
def handle_invalid_usage(error):
    return make_response(jsonify({'error': error.to_dict()}), 404)



if __name__ == '__main__':
    app.run()    