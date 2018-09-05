import pandas as pd
import numpy as np
import os, random, sys, pickle, time

from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from math import sqrt
from sklearn import tree

from common import Model, FeatureMap, FactorMap
from features import *

STOP_IF_NO_PROGRESS_AFTER_N_ITERATIONS = 20
ROUNDING_LEVEL_TO_COMPARE_METRIC = 4

def split(df, pct=.7):
    X_tr, X_xv = [], []
    
    #partition the data by season
    seasons   = df.Season.unique()
    teams     = df.posteam.unique()
    quarters  = df.qtr.unique()

    for season in seasons:
        df_season = df[df["Season"] == season]

        for team in teams:
            df_team = df_season[df_season["posteam"] == team]

            for quarter in quarters:
                subset = df_team[df_team["qtr"] == quarter]

                indices = [x for x in subset.index]
                random.shuffle(indices)

                for ind in indices:
                    if np.random.rand() <= pct:
                        X_tr.append(ind)
                    else:
                        X_xv.append(ind)

    return X_tr, X_xv

# reproducable script
random.seed(1)
np.random.seed(1)

#get the arguments form the commandline
datadir = "./data/regression"
modeldir = "./model/regression"

if not os.path.exists(datadir):
    os.makedirs(datadir)

if not os.path.exists(modeldir):
    os.makedirs(modeldir)    

#define the feature of the model
'''
Season              - The year of the season
qtr                 - The quarter of the game 
down                - The down of the play
ydstogo             - The number of yards to the first down
ScoreDiff           - The score difference of the team with possession and the defensive team
YdsToTD             - The number of yards to a touchdown
TimeLeftInQtr       - How much time is left in the quarter
PercentageOfField   - The area of the field of play in 20% increments
'''

classificationcols = [
    
]

floatcols = [
    'qtr',
    'down',
    'ydstogo',
    'YardsGainedOnPriorPlay' #This is a lookback feature
]

metacols = [
    "GameID",
    "posteam",
    "DefensiveTeam",
    "PlayType",    
    "SideofField",
    "HomeTeam",
    "AwayTeam",
    "yrdline100",
    "time",
    "TimeSecs",
    "RunPassPercentagePriorToPlay",
    "Season",
    'TimeUnder'
]

#The y colum has been precomputed in the dataset
ycol = "RunPassPercentagePriorToPlay"

allcols = floatcols + classificationcols + metacols

#load the csv into a dataframe
fpath = os.path.join("./data", "NFLPlays2009_2017.psv")

#reduce the dataset down to what we need for training
df = pd.read_csv(fpath, usecols=allcols, sep='|')
df = df[(df["PlayType"] == 'Run') | (df["PlayType"] == 'Pass')]
df = df[np.isfinite(df['down'])]

#computed columns
df["SideofField"] = df.apply(getsideoffield, axis=1)
df["PosTeam"] = df.apply(getposteamhomeaway, axis=1)
df["YdsToTD"] = df.apply(getydstotd, axis=1)
df["TimeLeftInQtr"] = df["time"].apply(timeleftinqtr)
df["TimeLeftInQtrInSecs"] = df.apply(timeleftinqtrinsecs, axis=1)
df["PctTimeLeftInQtr"] = df['TimeUnder'].apply(pcttimeleftinqtr)
df["PercentageOfField"] = df['yrdline100'].apply(percentageoffield)
df["RatioYrdsToGoTimeLeftInQtr"] = df.apply(getratioyrdstogototimeleftinqtr, axis=1)

#add the computed column to the classificationcols so we can label encode it
classificationcols = classificationcols + ["SideofField", "PosTeam"]
floatcols          = floatcols + ["YdsToTD", "TimeLeftInQtr", "PercentageOfField", "RatioYrdsToGoTimeLeftInQtr", "PctTimeLeftInQtr"]

#split the data 70/30
X_tr_indices, X_xv_indices = split(df)

traincols = floatcols + classificationcols

#build the X/Y matrices for training and xval
X_tr = df.ix[X_tr_indices, traincols].reset_index(drop=True)
Y_tr = df.ix[X_tr_indices, ycol].reset_index(drop=True)
tr_meta = df.ix[X_tr_indices, metacols].reset_index(drop=True)

X_xv = df.ix[X_xv_indices, traincols].reset_index(drop=True)
Y_xv = df.ix[X_xv_indices, ycol].reset_index(drop=True)
xv_meta = df.ix[X_xv_indices, metacols].reset_index(drop=True)

#label encode the categorical features
labelencoders = {}
for colname in classificationcols:
    
    le = LabelEncoder()
    vals = df[colname].unique()
    le.fit(vals)
    
    print("col:",colname,"values:",','.join(map(str,vals)))
    X_tr[colname]  = le.transform(X_tr[colname])
    X_xv[colname]  = le.transform(X_xv[colname])
    
    labelencoders[colname]     = le

#train the model
rfc = RandomForestRegressor(    
    max_depth=None,
    criterion="mse",
    min_samples_leaf=30,
    n_estimators=50,
    n_jobs=-1
)

rfc.fit(X_tr, Y_tr)

# eval on xval
start = time.time()
xv_yhat = rfc.predict(X_xv)
tr_yhat = rfc.predict(X_tr)
end = time.time()
print("elapsed time of predict in seconds", end - start)

xv_rmse = round(sqrt(mean_squared_error(Y_xv, xv_yhat)), ROUNDING_LEVEL_TO_COMPARE_METRIC)
tr_rmse = round(sqrt(mean_squared_error(Y_tr, rfc.predict(X_tr))), ROUNDING_LEVEL_TO_COMPARE_METRIC)

print("TRAIN RMSE: {0} XVAL RMSE {1}".format(tr_rmse, xv_rmse))

#print out the feature importance
importances = rfc.feature_importances_
std = np.std([tree.feature_importances_ for tree in rfc.estimators_],
             axis=0)
indices = np.argsort(importances)[::-1]

# Print the feature ranking
print("Feature ranking:")

for f in range(len(traincols)):
    print("%d. feature %s (%f)" % (f + 1, traincols[f], importances[indices[f]]))

#save the model to disk
Model.serialize(rfc, modeldir)

#serialize the features
FeatureMap.save(traincols, modeldir)

#serialize the Factors / Categorical variables
if len(labelencoders) > 0:
    FactorMap.save(labelencoders, modeldir)

# revert the float columns back to their string representations for writing out to a file
for colname in classificationcols:
    le = labelencoders[colname]
    X_xv[colname]  = le.inverse_transform(X_xv[colname])

#save results to file
outfilepath = os.path.join(datadir, "xvalpreictions.csv")
sep = ','
with open(outfilepath, "w+") as fp:
    #write out the headings
    headercols = traincols + metacols + ["y", "yhat"]
    fp.write(sep.join([x for x in headercols]) + '\n')

    #write out each row of the xval set
    for i in X_xv.index:
        tr_row      = X_xv.loc[i, :].values
        meta_row    = xv_meta.loc[i, :].values
        y           = Y_xv[i]
        yhat        = xv_yhat[i]
        
        rowcols =  [str(x) for x in tr_row] + [str(x) for x in meta_row] + [str(x) for x in [y, yhat]]
        fp.write(sep.join([x for x in rowcols]) + '\n')
        