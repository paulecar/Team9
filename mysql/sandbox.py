from team9 import create_app
team9 = create_app()
team9.app_context().push()
from team9.models import Player, Match, MatchUp, Season
from sqlalchemy import func
from team9 import db

player = Player.query.filter_by(idplayer=6).first()

select_history = db.session.query(Match, MatchUp, Season, Player). \
    join(MatchUp, Match.idmatch == MatchUp.Match_ID). \
    join(Season, Match.Season_ID == Season.idseason). \
    join(Player, MatchUp.Player_ID == Player.idplayer). \
    filter(MatchUp.Player_ID == 6, Season.idseason == 12). \
    order_by(Match.MatchDate).all()

print(select_history)
