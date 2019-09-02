from team9 import create_app
team9 = create_app()
team9.app_context().push()

from team9.models import Season, Match, Result, Player, Match, MatchUp
from sqlalchemy import func
from team9 import db

def history():
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


def main():
    scores()


def scores():
    # Current matchup details to display in progress match
    results = db.session.query(Player, MatchUp, Match).join(MatchUp, Player.idplayer == MatchUp.Player_ID). \
        join(Match, Match.idmatch == MatchUp.Match_ID).filter_by(idmatch=185).order_by(MatchUp.idmatchup).all()

    max_racks = 0
    us = 0
    them = 0
    us_avail = 0
    them_avail = 0
    losses =0
    if len(results) == 4:
        for r in results:
            max_racks = max_racks + r.MatchUp.MatchUpRace
            us = us + r.MatchUp.MyPlayerScore
            them = them + r.MatchUp.OpponentScore

            if r.MatchUp.WinLose == "I":
                us_avail = us_avail + (r.MatchUp.MatchUpRace - r.MatchUp.MyPlayerScore)
                them_avail = them_avail + (r.MatchUp.MatchUpRace - r.MatchUp.OpponentScore)
            if r.MatchUp.WinLose == "L":
                losses += 1

    print(max_racks, us, them, us_avail, them_avail, us + us_avail, them + them_avail, losses)

    if (us + us_avail) < them or losses > 2:
        print("we cannot win")
    elif us > (them + them_avail):
        print("they cannot win")
    elif ((us + us_avail) - them) == 0:
        print("only a draw available")
    else:
        print("all to play for")
        margin = (us + us_avail) - (them)
        print("but we can lose", margin - 1, "more and still win -", margin, "to draw")


if __name__ == "__main__":
    main()