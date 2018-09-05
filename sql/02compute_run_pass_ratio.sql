
select x3.*, x3.TotalRun/NULLIF(((x3.TotalRun + x3.TotalPass) * 1.0), 0) 'RunPassRatio'
from
(
select x1.curgameid 'GameId', x1.curplayid 'PlayID', x1.curposteam 'posteam', x1.drive, x1.down, x1.qtr, x1.currentplay 'Play', x1.TimeLeft, sum(x2.PrevIsPass) 'TotalPass', sum(x2.PrevIsRun) 'TotalRun' 
from lookback x1
inner join lookback x2
    on x2.curgameid = x1.curgameid
    and x2.curposteam = x1.curposteam
    and x2.prevplayid < x1.curplayid    
group by  x1.curgameid,  x1.curposteam,  x1.drive, x1.down, x1.qtr, x1.curplayid, x1.TimeLeft, x1.currentplay
) as x3
order by x3.GameId, x3.posteam, x3.PlayID, x3.Play