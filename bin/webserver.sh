#! /bin/bash

#run the code in a virtual environment
python -m venv .venv
source .venv/bin/activate

#install dependencies from the requirements file if it exists
if [ -e requirements.txt ]
then
    pip install -r requirements.txt
else
    pip install numpy scipy scikit-learn pandas flask
fi

#uncomment this line to set the flask web server into debug mode
#export FLASK_ENV=development

python python/webserver.py

#save the requirements.txt if it does NOT exist
if [ ! -f requirements.txt ]; then
    pip freeze >> requirements.txt
fi

deactivate