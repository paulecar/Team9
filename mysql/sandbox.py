from team9 import create_app
team9 = create_app()
team9.app_context().push()
from team9.models import Player, Match, MatchUp
from sqlalchemy import func
from team9 import db


playoff_summary = db.session.query(Player.idplayer, Player.FirstName, Player.Surname, Player.Active,
                                   func.count(MatchUp.idmatchup).label('MatchesPlayed'),
                                   func.sum(MatchUp.MyPlayerActual).label('ActRacksWon'),
                                   func.sum(MatchUp.OpponentActual).label('ActRacksLost'),
                                   (func.sum(MatchUp.MyPlayerActual) / (func.sum(MatchUp.OpponentActual) + func.sum(
                                       MatchUp.MyPlayerActual))).label('RackPct'),
                                   (func.sum(func.IF(MatchUp.WinLose == 'W', 1, 0)) / func.count(
                                       MatchUp.WinLose)).label('WinPct')). \
    join(MatchUp, MatchUp.Player_ID == Player.idplayer). \
    join(Match, MatchUp.Match_ID == Match.idmatch). \
    filter_by(PlayOff="Y"). \
    order_by(Player.Surname).group_by(Player.idplayer).all()

print(playoff_summary)