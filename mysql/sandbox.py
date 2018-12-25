from team9 import create_app
team9 = create_app()
team9.app_context().push()
from team9 import db
from team9.models import Season, Availability, Player, Match, Result
import copy

season = Season.query.filter_by(CurrentSeason='Y').first()

matches = db.session.query(Match, Result).outerjoin(Result, Result.Match_ID == Match.idmatch). \
    filter(Match.Season_ID == season.idseason).order_by(Match.MatchDate.asc()).all()

players = Player.query.filter_by(Active="Y").order_by(Player.Surname).all()
avail = Availability.query.filter_by(Season_ID=season.idseason).all()

player_list = []
for player in players:
    player_list.append({'initials': player.FirstName[0] + player.Surname[0], 'id': player.idplayer, 'avail' : True})

print(avail)
print(matches)

avail_map={}

for m in matches:
    if not m.Result:
        avail_map[m.Match.idmatch] = copy.deepcopy(player_list)
        for p in avail_map[m.Match.idmatch]:
            for a in avail:
                if a.Match_ID == m.Match.idmatch and a.Player_ID == p['id']:
                    print("Bingo:", a.Match_ID, m.Match.idmatch, a.Player_ID, p['id'])
                    p['avail'] = False
                    p['a_id'] = a.idavailability

print(player_list)
for k, v in avail_map.items():
    print(k, v)
