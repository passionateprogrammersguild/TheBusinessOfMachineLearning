import pandas as pd
import math


'''
GameID	Drive	posteam	PlayType
2009091000	1	PIT	Kickoff - 0.0
2009091000	1	PIT	Pass    - 0.0
2009091000	1	PIT	Run     - 
2009091000	1	PIT	Pass
2009091000	1	PIT	Punt
2009091000	2	TEN	Run
2009091000	2	TEN	Pass
2009091000	2	TEN	Run
'''
def computerunpercentage(prevrow, currow, prevruncount, prevpasscount):
    
    result = 0.0

    if prevrow is None:
        return result

    if prevruncount == 0 and prevpasscount == 0:
        return result

    result = prevruncount / (prevruncount +  prevpasscount)

    return 0.0 if math.isnan(result) else result

def computeyardsgainedonpriorplay(prev2rows, currow):
    if prev2rows is None:
        return 0.0

    posteam = currow['posteam']

    #make sure the previous two rows are for the team that has possession of the ball
    if all(x==posteam for x in prev2rows) == False:
        return 0.0

    #compute the yards gained from teh previous two plays
    ydsgainedonpriorplay = prevrow[1]['yrdline100'] - prevrow[0]['yrdline100']

    print("yds gained {0} gameid {1} posteam {2} timeinsecs {3}".format(ydsgainedonpriorplay,currow['GameID'], currow['posteam'], currow['TimeSecs']))

    return ydsgainedonpriorplay

df = pd.read_csv("./data/NFL Play by Play 2009-2017.csv")

#TODO:  create a new column for the run/pass percentage so far in the game
df_sorted = df.sort_values(['GameID', 'TimeSecs'], ascending=[True, False])
#df_sorted = df_sorted[(df_sorted["GameID"] == 2009091000) | (df_sorted["GameID"] == 2009091300)]
prevrow       = None
gamecounts    = {}
runpercentages = []
yardsgainedonpriorplay = []
prev2rows = []
#TODO create more lookback features

firstgame = df_sorted.loc[0, ["posteam", "DefensiveTeam"]]
print("processing first game of the {0} v.s. {1}".format(firstgame["posteam"], firstgame["DefensiveTeam"]))
for index, row in df_sorted.iterrows():

    #if the game id has changed then we need to reset our counters
    if prevrow is not None:
        if prevrow["GameID"] != row["GameID"]:
            print("New Game resetting game counts for the {0} v.s. {1}".format(row["posteam"], row["DefensiveTeam"]))
            gamecounts = {}
    
    #initialize the lookup table for the run pass counts per team with possession of the ball
    posteam = row["posteam"]
    if posteam not in gamecounts:
        gamecounts[posteam] = {"prevruncount": 0, "prevpasscount": 0}

    #calculate the run/pass ratio for the current play    
    runpercentage = computerunpercentage(prev2rows, row, gamecounts[posteam]["prevruncount"], gamecounts[posteam]["prevpasscount"])
    runpercentages.append(runpercentage)

    #yards gained on the prior play
    yardsgainedonpriorplay.append(computeyardsgainedonpriorplay(prevrow, row))

    #print("drive {0} posteam {1} playtype {2} prevruncount {3} prevpascount {4} runpctg {5}", row["Drive"], row["posteam"], row["PlayType"], gamecounts[posteam]["prevruncount"], gamecounts[posteam]["prevpasscount"], runpercentage)
    
    #compute the counts for the team with posession of the ball based on the current play
    playtype = row["PlayType"]
    if playtype == "Run":
        gamecounts[posteam]["prevruncount"] +=1

    if playtype == "Pass":
        gamecounts[posteam]["prevpasscount"] +=1

    prevrow = row
    if len(prev2rows) == 2:
        prev2rows = []
        prev2rows.append(prevrow)

df_sorted["RunPassPercentagePriorToPlay"] = runpercentages
df_sorted["YardsGainedOnPriorPlay"] = yardsgainedonpriorplay

df_sorted.to_csv("./data/NFLPlays2009_2017.psv", sep='|')