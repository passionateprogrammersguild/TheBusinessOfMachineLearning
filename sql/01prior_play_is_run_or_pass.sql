--calculate the sum where the the gameid = gameid the posteam = posteam and the prevplayid < curplayid
IF OBJECT_ID('dbo.lookback', 'U') IS NOT NULL 
  DROP TABLE dbo.lookback; 

select x1.GameID 'prevgameid', 
       x0.GameID 'curgameid',
       x1.PlayID 'prevplayid',
       x0.PlayID 'curplayid',
       x1.posteam 'prevposteam', 
       x0.posteam 'curposteam',
       x1.PlayType 'PrevPlay', 
       x0.PlayType 'CurrentPlay',
       x0.drive,
       x0.qtr,
       x0.down,
       cast(replace(cast(cast(x0.[time] as time) as varchar(5)), ':', '.') as float) 'TimeLeft',
       isnull(x1.IsRun, 0) 'PrevIsRun', 
       isnull(x1.IsPass, 0) 'PrevIsPass'
into lookback 
from (
select
    posteam,
    gameid, 
    drive,    
    down,
    qtr,
    timesecs,
    playtype,
    [time],
    row_number() over (partition by posteam, gameid order by timesecs desc) as PlayID,
    CASE when playtype = 'Run' then 1 else 0 end 'IsRun',
    CASE when playtype = 'Pass' then 1 else 0 end 'IsPass'
from NFLPlays2009_2017
where posteam is not null
) x0
left join (
select
    posteam,
    gameid, 
    drive, 
    down,
    qtr,
    timesecs,
    playtype,
    [time],
    row_number() over (partition by posteam, gameid order by timesecs desc) as PlayID,
    CASE when playtype = 'Run' then 1 else 0 end 'IsRun',
    CASE when playtype = 'Pass' then 1 else 0 end 'IsPass'
from NFLPlays2009_2017
) x1 on x0.posteam = x1.posteam and x0.GameID = x1.GameID and x0.PlayID = x1.PlayID+1