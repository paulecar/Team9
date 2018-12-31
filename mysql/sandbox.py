from team9 import create_app
team9 = create_app()
team9.app_context().push()
from team9.models import Season, Match, Result
from sqlalchemy import func
from team9 import db

season_history = db.session.query(Season.idseason, Season.SeasonName, Season.SeasonStart, Season.SeasonEnd,
                                  func.count(Match.idmatch).label('MatchesPlayed'),
                                  func.sum(func.IF(Result.DidWeWin == 1, 1, 0)).label('Wins'),
                                  func.sum(func.IF(Result.DidWeWin == 0, 1, 0)).label('Losses')). \
    join(Match, Match.Season_ID == Season.idseason). \
    join(Result, Result.Match_ID == Match.idmatch). \
    group_by(Season.idseason, Season.SeasonName, Season.SeasonStart, Season.SeasonEnd). \
    order_by(Season.SeasonStart.desc()).all()

for season in season_history:
    print(season.SeasonName, season.MatchesPlayed, season.Wins, season.Losses)