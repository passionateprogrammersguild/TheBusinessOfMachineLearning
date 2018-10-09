#! /bin/bash

logdir="reports"
rootfilename=$(date +"%Y%m%d%H%M")
mkdir -p $logdir
mkdir -p data
mkdir -p model

python -m venv .venv
source .venv/bin/activate

if [ ! -f 'data/NFL Play by Play 2009-2017.csv' ]; then
    echo "ERROR:  file data/NFL Play by Play 2009-2017.csv does not exist.  Download from https://www.kaggle.com/maxhorowitz/nflplaybyplay2009to2016/version/5 and place in the data folder with the file name NFL Play by Play 2009-2017.csv" 1>&2
    exit 64
fi

if [ -e requirements.txt ]
then
    pip install -r requirements.txt
else
    pip install numpy scipy sklearn pandas
fi

(python python/prepare_psv.py 2>&1 | tee ./$logdir/$rootfilename-prepare_psv.log)

#save the requirements.txt if it does NOT exist
if [ ! -f requirements.txt ]; then
    pip freeze >> requirements.txt
fi

deactivate