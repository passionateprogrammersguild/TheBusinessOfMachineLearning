logdir="reports"
rootfilename=$(date +"%Y%m%d%H%M")
mkdir -p $logdir

if [ ! -f 'data/NFLPlays2009_2017.psv' ]; then
    echo "ERROR:  file data/NFLPlays2009_2017.psv does not exist.  Please run bash bin/run_prepare.sh" 1>&2
    exit 64
fi

#! /bin/bash

#run the code in a virtual environment
python -m venv .venv
source .venv/bin/activate

#install dependencies from the requirements file if it exists
if [ -e requirements.txt ]
then
    pip install -r requirements.txt
else
    pip install numpy scipy sklearn pandas
fi

(python python/01train_multiclass.py 2>&1 | tee ./$logdir/$rootfilename-multiclass.log)
(python python/02train_regression.py 2>&1 | tee ./$logdir/$rootfilename-regression.log)
(python python/03train_binaryclassifier.py 2>&1 | tee ./$logdir/$rootfilename-binaryclassifier.log)

#save the requirements.txt if it does NOT exist
if [ ! -f requirements.txt ]; then
    pip freeze >> requirements.txt
fi

deactivate