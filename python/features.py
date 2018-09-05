
def timeleftinqtr(val):
    return  float(val.replace(':', '.'))

def getydstotd(row):
    return 100 - row["yrdline100"]

def getratioyrdstogototimeleftinqtr(row):
    if row["TimeLeftInQtr"] == 0:
        return 0

    return row["ydstogo"] / (row["TimeLeftInQtr"] * 1.0)

def getposteamhomeaway(row):
    if row["posteam"] == row["HomeTeam"]:
        return "HomeTeam"

    if row["posteam"] == row["AwayTeam"]:
        return 'AwayTeam'   
    
    raise Exception("Invalid value of " + row["posteam"])

'''
Based on the yardline return a number representing the percentage of the field the posteam has the ball
The field will be divided into 20% increments and will have a binary number representing the 5 positions
10000 - means the percentage of field is in the first 20% meaning 0-20 year line
01000 - 21-40
00100 - 41-60
00010 - 61-80
00001 - 81
'''
def percentageoffield(yrdline100):
  
    if yrdline100 < 21:
        return .20
    if yrdline100 >= 21 and yrdline100 <= 40:
        return .40
    if yrdline100 >= 41 and yrdline100 <= 60 :
        return .60
    if yrdline100 >= 61 and yrdline100 <= 80 :
        return .80

    return 1.0

def getsideoffield(row):
    if row["SideofField"] == row["posteam"]:
        return "PosTeam"

    if row["SideofField"] == row["DefensiveTeam"]:
        return 'DefensiveTeam'

    if row["SideofField"] == "Mid" or row["SideofField"] == "MID":
        return 'Mid'

    raise Exception("Invalid value of " + row["SideofField"])

def pcttimeleftinqtr(value):
    return value/ 15.0

def timeleftinqtrinsecs(row):
    #1st qtr 3600 - 2700
    #2nd qtr 2700 - 1800
    #3rd qtr 1800 - 900
    #4th qtr 900  - 0
    #5th qtr 0    - 900

    qtr = row["qtr"]
    t   = row["TimeSecs"]

    if qtr == 1:
        return abs(t - 2700)

    if qtr == 2:
        return abs(t - 1800)

    if qtr == 3:
        return abs(t - 900)
    
    if qtr == 4:
        return t

    return 900 - t
