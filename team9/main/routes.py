from flask import render_template, flash, redirect, url_for, current_app
from team9 import db
from team9.models import Player, Match, Season, MatchUp, Result, Availability
from team9.main.forms import LiveScore
from team9utils import hcaps
from flask_login import current_user, login_required
from sqlalchemy import func
import pygal, copy
from team9.main import bp
from team9utils import getRace, setWinner, get_est, kvmGet

# Common update logic for livescores and '+' button updates
def apply_MatchUpUpdates(match, playerscore, opponentscore, math_elim):

    # Get race details so we can calculate 'actual' racks won/lost
    wire, oppwire, race = getRace(match.MyPlayerRank, match.OpponentRank)

    result = setWinner(race,
                       playerscore,
                       opponentscore,
                       math_elim)

    # Build new MatchUp record
    matchup = MatchUp(OpponentName=match.OpponentName,
                      MyPlayerRank=match.MyPlayerRank,
                      OpponentRank=match.OpponentRank,
                      Player_ID=match.Player_ID,
                      MatchUpRace=match.MatchUpRace,
                      MyPlayerWire=match.MyPlayerWire,
                      MyPlayerScore=playerscore,
                      OpponentScore=opponentscore,
                      Match_ID=match.Match_ID,
                      MyPlayerActual=playerscore - wire,
                      OpponentActual=opponentscore - oppwire,
                      WinLose=result)

    # Delete existing MatchUp and create a new one (this fires trigger to create a 'Result')
    MatchUp.query.filter_by(idmatchup=match.idmatchup).delete()
    db.session.add(matchup)
    db.session.commit()

    return


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = get_est()
        db.session.commit()


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    # Get current season
    season = Season.query.filter_by(CurrentSeason='Y').first()

    # TODO Consider removing views entirely and writing SQLALchemy query
    # Players query populates the Bog - query using 'execute' because 'the_bog' is a view
    players = db.session.execute("SELECT b.Season_ID, p.idplayer, CONCAT(p.FirstName, ' ', p.Surname) as Name, "
                                        "b.Lose, b.Win, b.Losses, b.Played, p.Bogged, p.BoggedDate "
                                 "FROM amsterdamteam9.the_bog b "
                                 "RIGHT JOIN amsterdamteam9.player p ON b.idplayer = p.idplayer "
                                 "WHERE p.Active = 'Y' "
                                 "ORDER BY p.Bogged, p.BoggedDate, b.Lose, b.Losses, b.Played").fetchall()

    # Nextmatch - speaks for itself
    nextmatch = Match.query.order_by(Match.MatchDate.asc(), Match.StartTime.asc()).\
        filter(Match.MatchOver == None).first()

    # Check to see we have a current/future match, otherwise look for the last match
    if not nextmatch:
        nextmatch = Match.query.order_by(Match.MatchDate.desc(), Match.StartTime.desc()).first()

    # Extract availability for the nextmatch only and create list of absentees
    avail = Availability.query.filter_by(Match_ID=nextmatch.idmatch).all()
    absent={}
    for a in avail:
        absent[a.Player_ID] = a.idavailability

    # Current matchup details to display in progress match
    results = db.session.query(Player, MatchUp, Match).join(MatchUp, Player.idplayer == MatchUp.Player_ID). \
        join(Match, Match.idmatch == MatchUp.Match_ID).filter_by(idmatch=nextmatch.idmatch).order_by(Player.FirstName).all()

    # Look for match in progress to determine whether to show the 'match over' button
    match_inprogress = False

    for matchup in results:
        if matchup.MatchUp.WinLose == "I":
            match_inprogress = True

    if len(results) < 4:
        match_inprogress = True

    # Used for tacking live scores
    live = db.session.query(Result).filter_by(Match_ID=nextmatch.idmatch).first()
    return render_template('index.html', season=season,
                           players=players, nextmatch=nextmatch, absent=absent,
                           captainsMessage=kvmGet('CAPTAINSMESSAGE'),
                           results=results, live=live, helper_role="on",
                           hcaps=hcaps, inprogress=match_inprogress)


@bp.route('/ranking')
@bp.route('/ranking/<season_id>/<season_name>')
def ranking(season_id=None, season_name=None):
    # If no season is passed as argument - use the current season
    if season_id is None:
        # Get current season
        season = Season.query.filter_by(CurrentSeason='Y').first()
        query_season = season.idseason
        display_season_name = season.SeasonName
    else:
        query_season = season_id
        display_season_name = season_name

    base_query = "SELECT * FROM AmsterdamTeam9.player_ranking WHERE idseason = {} ".format(query_season)

    # TODO Consider removing views entirely and writing SQLALchemy query
    # Three separate queries to satisfy sort order - 'execute' used because 'player_ranking' is a view
    # This was probably done this way becuase I hadn't figured out how to use 'func' for calculated columns
    rankings_matchpct = db.session.execute(base_query + "ORDER BY MatchPct Desc, RacksPct Desc, ActPct Desc").fetchall()
    rankings_rackspct = db.session.execute(base_query + "ORDER BY RacksPct Desc, MatchPct Desc, ActPct Desc").fetchall()
    rankings_actpct =   db.session.execute(base_query + "ORDER BY ActPct Desc, MatchPct Desc, RacksPct Desc").fetchall()
    return render_template('rank.html',
                           season=display_season_name,
                           rankings1=rankings_matchpct,
                           rankings2 = rankings_rackspct,
                           rankings3 = rankings_actpct)


@bp.route('/pickseason/<pick>')
@login_required
def pickseason(pick):
    seasons = Season.query.order_by(Season.SeasonStart.asc()).all()
    return render_template('pickseason.html', seasons=seasons, pick=pick)


@bp.route('/history')
@bp.route('/history/<player_id>')
@login_required
def history(player_id=None):
    if current_user.Player_ID is None and player_id is None:
        return redirect(url_for('main.index'))

    if player_id:
        p = player_id
    else:
        p = current_user.Player_ID

    player_detail = db.session.query(Player.Surname, MatchUp.OpponentRank,
                     func.count(MatchUp.idmatchup).label('MatchesPlayed'),
                     func.sum(MatchUp.MyPlayerActual).label('ActRacksWon'),
                     func.sum(MatchUp.OpponentActual).label('ActRacksLost'),
                     (func.sum(MatchUp.MyPlayerActual) / (func.sum(MatchUp.OpponentActual) + func.sum(MatchUp.MyPlayerActual))).label('RackPct'),
                     (func.sum(func.IF(MatchUp.WinLose == 'W', 1, 0)) / func.count(MatchUp.WinLose)).label('WinPct')). \
        join(MatchUp, MatchUp.Player_ID == Player.idplayer).group_by(MatchUp.OpponentRank). \
        filter_by(Player_ID=p).order_by(MatchUp.OpponentRank).all()

    player_graph = db.session.query(Season.SeasonName, Season.SeasonStart, Season.idseason,
                                    func.count(MatchUp.idmatchup).label('MatchesPlayed'),
                                    func.sum(func.IF(MatchUp.WinLose == 'W', 1, 0)).label('Wins'),
                                    func.sum(func.IF(MatchUp.WinLose == 'L', 1, 0)).label('Loses'),
                                    (func.sum(func.IF(MatchUp.WinLose == 'W', 1, 0)) / func.count(MatchUp.WinLose)).label('WinPct'),
                                    Player.idplayer). \
        join(Match, Season.idseason == Match.Season_ID). \
        join(MatchUp, Match.idmatch == MatchUp.Match_ID). \
        join(Player, MatchUp.Player_ID == Player.idplayer). \
        filter_by(idplayer=p). \
        group_by(Player.idplayer, Season.SeasonName, Season.SeasonStart, Season.idseason). \
        order_by(Season.SeasonStart).all()

    # Configure horizontal bar chart of player history against the wire
    chart = pygal.HorizontalStackedBar(show_legend=False, tooltip_fancy_mode=False,
                                       print_values=True, width=800, height=300)

    labels=[]
    wins=[]
    loses=[]
    # Create series lists for the chart.add command
    # PYGAL_URL is localhost:5000 for testing, main URL for AWS
    for season in player_graph:
        labels.append(season.SeasonName)
        wins.append({'value' : int(season.Wins), 'color': 'MediumSeaGreen',
                     'xlink' : { 'href' : '{}{}'.format(current_app.config['PYGAL_URL'],
                                url_for('main.drilldown', player_id=season.idplayer,
                                        season_id=season.idseason, win_loss='W')),
                                'target' : '_parent' },
                     'label' : "Pct {:.0%}".format(season.WinPct)})
        loses.append({'value' : int(season.Loses), 'color': 'Orange',
                      'xlink': {'href': '{}{}'.format(current_app.config['PYGAL_URL'],
                                url_for('main.drilldown', player_id=season.idplayer,
                                        season_id=season.idseason, win_loss='L')),
                                'target': '_parent'},
                      'label' : "Pct {:.0%}".format(1 - season.WinPct)})

    # Build the graph itself
    chart.x_labels = labels
    chart.add("Wins", wins)
    chart.add("Loses", loses)
    chart = chart.render_data_uri()

    player_summary = db.session.query(Player.Surname, MatchUp.MyPlayerRank,
                    func.count(MatchUp.idmatchup).label('MatchesPlayed'),
                    func.sum(MatchUp.MyPlayerActual).label('ActRacksWon'),
                    func.sum(MatchUp.OpponentActual).label('ActRacksLost'),
                    (func.sum(MatchUp.MyPlayerActual) / (func.sum(MatchUp.OpponentActual) + func.sum(MatchUp.MyPlayerActual))).label('RackPct'),
                    (func.sum(func.IF(MatchUp.WinLose == 'W', 1, 0)) / func.count(MatchUp.WinLose)).label('WinPct')). \
        join(MatchUp, MatchUp.Player_ID == Player.idplayer).group_by(MatchUp.MyPlayerRank).filter_by(Player_ID=p).all()

    player = Player.query.filter_by(idplayer=p).first()

    player_history = db.session.query(Match, MatchUp). \
        join(MatchUp, Match.idmatch == MatchUp.Match_ID). \
        filter(MatchUp.Player_ID == p). \
        order_by(Match.MatchDate).all()

    return render_template('history.html', history=player_history, player=player, details=player_detail,
                           summary=player_summary, chart=chart)


@bp.route('/drilldown/<player_id>/<season_id>/<win_loss>')
@login_required
def drilldown(player_id=None, season_id=None, win_loss=None):
    if player_id is None or season_id is None or win_loss is None:
        return redirect(url_for('main.index'))

    if player_id:
        p = player_id
    else:
        p = current_user.Player_ID

    player = Player.query.filter_by(idplayer=p).first()

    select_history = db.session.query(Match, MatchUp). \
        join(MatchUp, Match.idmatch == MatchUp.Match_ID). \
        filter(MatchUp.Player_ID == player_id, Match.Season_ID == season_id, MatchUp.WinLose == win_loss). \
        order_by(Match.MatchDate).all()

    return render_template('drilldown.html', history=select_history, player=player)


@bp.route('/team/<team>')
@login_required
def team(team):
    team_history = db.session.query(Result, MatchUp, Player, Match).join(MatchUp, MatchUp.Match_ID == Result.Match_ID). \
        join(Player, Player.idplayer == MatchUp.Player_ID).join(Match, Match.idmatch == MatchUp.Match_ID). \
        filter_by(OpposingTeam=team).order_by(Match.MatchDate.desc()).all()

    # Check to see if latest match is still in progress
    match_inprogress = False
    for match in team_history:
        if match.Match.idmatch != team_history[0].Match.idmatch:
            break
        if match.MatchUp.WinLose == "I":
            match_inprogress = True
            break

    return render_template('team.html', history=team_history, team=team, inprogress=match_inprogress)


@bp.route('/opponent/<opp>')
@login_required
def opponent(opp):
    opp_history = db.session.query(Match, MatchUp, Player).\
        join(MatchUp, Match.idmatch == MatchUp.Match_ID).filter_by(OpponentName=opp). \
        join(Player, Player.idplayer == MatchUp.Player_ID).order_by(Match.MatchDate.desc()).all();
    return render_template('opponent.html', history=opp_history, opp=opp)


@bp.route('/results')
@bp.route('/results/<season_id>/<season_name>')
@login_required
def results(season_id=None, season_name=None):
    # If no season is passed as argument - use the current season
    if season_id is None:
        # Get current season
        season = Season.query.filter_by(CurrentSeason='Y').first()
        query_season = season.idseason
        display_season_name = season.SeasonName
    else:
        query_season = season_id
        display_season_name = season_name

    matches = db.session.query(Match, Result).outerjoin(Result, Result.Match_ID == Match.idmatch). \
        filter(Match.Season_ID == query_season).order_by(Match.MatchDate.asc()).all()

    # Calculate pie and season info
    wins=0
    loses=0
    season_info={'w_skunk':0, 'l_skunk':0, 'w_1ptr':0, 'l_1ptr':0, 'w_tb':0, 'l_tb':0}
    for match in matches:
        if match.Match.MatchOver:
            diff = match.Result.RacksWon - match.Result.RacksLost
            skunk = match.Result.MatchUpsWon - match.Result.MatchUpsLost
            cnt = match.Result.MatchUpsWon + match.Result.MatchUpsLost
            if match.Result.DidWeWin == 1:
                wins = wins+1
                if skunk == 4:  season_info['w_skunk'] = season_info['w_skunk'] + 1
                if diff == 1:   season_info['w_1ptr'] = season_info['w_1ptr'] + 1
                if cnt == 5:    season_info['w_tb'] = season_info['w_tb'] + 1
            else:
                loses=loses+1
                if skunk == -4: season_info['l_skunk'] = season_info['l_skunk'] + 1
                if diff == -1:  season_info['l_1ptr'] = season_info['l_1ptr'] + 1
                if cnt == 5:    season_info['l_tb'] = season_info['l_tb'] + 1


    # Build the pie
    chart = pygal.Pie(half_pie=True, show_legend=False, inner_radius=0.4,
                      tooltip_fancy_mode=True, print_values=True, width=800, height=300)
    # Make sure we have at least one match
    if wins+loses >=1 :
        chart.add('Wins', [{'value': wins/(wins+loses) * 100, 'color' : 'MediumSeaGreen'}],
                  formatter = lambda x: "Wins {:.0%}({})".format(x/100, wins))
        chart.add('Loses', [{ 'value' : loses/(wins+loses) * 100, 'color' : 'Orange'}],
                  formatter = lambda x: "Loses {:.0%}({})".format(x/100, loses))
    chart = chart.render_data_uri()

    return render_template('results.html', matches=matches, season=display_season_name, chart=chart, info=season_info)


@bp.route('/availability')
@login_required
def availability():
    # Get current season
    season = Season.query.filter_by(CurrentSeason='Y').first()

    matches = db.session.query(Match, Result).outerjoin(Result, Result.Match_ID == Match.idmatch). \
        filter(Match.Season_ID == season.idseason).order_by(Match.MatchDate.asc()).all()

    players = Player.query.filter_by(Active="Y").order_by(Player.Surname).all()
    avail = Availability.query.filter_by(Season_ID=season.idseason).all()

    player_list = []
    for player in players:
        player_list.append({'initials': player.FirstName[0] + player.Surname[0], 'id': player.idplayer, 'avail': True})

    avail_map = {}
    for m in matches:
        if not m.Result:
            avail_map[m.Match.idmatch] = copy.deepcopy(player_list)
            for p in avail_map[m.Match.idmatch]:
                for a in avail:
                    if a.Match_ID == m.Match.idmatch and a.Player_ID == p['id']:
                        p['avail'] = False
                        p['a_id'] = a.idavailability

    return render_template('available.html', matches=matches, season=season.SeasonName,
                           players=player_list, avail=avail_map, seasonid=season.idseason)


@bp.route('/available/<availid>/<player>')
@login_required
def available(availid, player):
    Availability.query.filter_by(idavailability=availid).delete()

    flash('Availability for {} updated'.format(player))

    db.session.commit()

    if len(player) == 2:
        target='main.availability'
    else:
        target='main.index'

    return redirect(url_for(target))


@bp.route('/unavailable/<playerid>/<matchid>/<seasonid>/<player>')
@login_required
def unavailable(playerid, matchid, seasonid, player):
    avail = Availability(Match_ID=matchid, Player_ID=playerid, Season_ID=seasonid)
    db.session.add(avail)

    flash('Availability for {} updated'.format(player))

    db.session.commit()

    if len(player) == 2:
        target='main.availability'
    else:
        target='main.index'

    return redirect(url_for(target))


@bp.route('/lifetime')
@login_required
def lifetime():
    player_summary = db.session.query(Player.idplayer, Player.FirstName, Player.Surname, Player.Active,
                  func.count(MatchUp.idmatchup).label('MatchesPlayed'),
                  func.sum(MatchUp.MyPlayerActual).label('ActRacksWon'),
                  func.sum(MatchUp.OpponentActual).label('ActRacksLost'),
                  (func.sum(MatchUp.MyPlayerActual) / (func.sum(MatchUp.OpponentActual) + func.sum(MatchUp.MyPlayerActual))).label('RackPct'),
                  (func.sum(func.IF(MatchUp.WinLose == 'W', 1, 0)) / func.count(MatchUp.WinLose)).label('WinPct')). \
        join(MatchUp, MatchUp.Player_ID == Player.idplayer).group_by(Player.idplayer).all()
    return render_template('lifetime.html', summary=player_summary)


@bp.route('/matchresult/<matchid>')
@login_required
def matchresult(matchid):
    results = db.session.query(Player, MatchUp, Match).join(MatchUp, Player.idplayer == MatchUp.Player_ID). \
        join(Match, Match.idmatch == MatchUp.Match_ID).filter_by(idmatch=matchid).all()
    return render_template('matchresult.html', results=results, helper_role="off", hcaps=hcaps)


@bp.route('/livescore/<matchupid>', methods=['GET', 'POST'])
@login_required
def livescore(matchupid):
    if current_user.UserRole != 'Admin' and current_user.UserRole != 'Helper':
        return redirect(url_for('main.index'))

    # Get Current MatchUp for update
    matchup = MatchUp.query.filter_by(idmatchup=matchupid).first()
    match = Match.query.filter_by(idmatch=matchup.Match_ID).first()
    ip = True
    if match.MatchOver == "Y":
        ip = False
    form = LiveScore(playerscore=matchup.MyPlayerScore, opponentscore=matchup.OpponentScore,
                     in_progress=ip, opponentrank=matchup.OpponentRank, playerrank=matchup.MyPlayerRank)

    # Note: the in_progress flag simply modifies validation behaviour
    # The value is NOT stored in the MatchUp table
    if form.validate_on_submit():

        apply_MatchUpUpdates(matchup, form.playerscore.data, form.opponentscore.data, form.mathematical_elimination.data)

        flash('Updated MatchUp - Match versus {} is now {} : {}'.
              format(matchup.OpponentName, form.playerscore.data, form.opponentscore.data))

        return redirect(url_for('main.index'))

    # Renders on the GET of when the input does not validate
    return render_template('livescore.html', title='Update Score', form=form, action='Update')


@bp.route('/updatematchup/<matchupid>/<player>', methods=['GET', 'POST'])
@login_required
def updatematchup(matchupid, player):
    if current_user.UserRole != 'Admin' and current_user.UserRole != 'Helper':
        return redirect(url_for('main.index'))

    # Get Current MatchUp for update
    match = MatchUp.query.filter_by(idmatchup=matchupid).first()
    opponentname = match.OpponentName

    # Get race details so we can later calculate 'actual' racks won/lost
    race = hcaps[match.MyPlayerRank][match.OpponentRank]

    # First check whether the match is already over
    if match.MyPlayerScore == race[1] or match.OpponentScore == race[1]:
        flash('Score updated - Match versus {} is already over.'.
              format(match.OpponentName))
        return redirect(url_for('main.index'))

    # Test the arguments to see which score to update
    if player == 'MY':
        playerscore = match.MyPlayerScore + 1
        opponentscore = match.OpponentScore
    else:
        playerscore = match.MyPlayerScore
        opponentscore = match.OpponentScore + 1

    apply_MatchUpUpdates(match, playerscore, opponentscore, False)

    flash('Score updated - Match versus {} - Score {}:{}'.
         format(opponentname, playerscore, opponentscore))

    return redirect(url_for('main.index'))


@bp.route('/deletematchup/<matchupid>/<matchid>', methods=['GET', 'POST'])
@login_required
def deletematchup(matchupid, matchid):
    if current_user.UserRole != 'Admin' and current_user.UserRole != 'Helper':
        return redirect(url_for('main.index'))

    MatchUp.query.filter_by(idmatchup=matchupid).delete()

    # TODO At some point, replace the trigger and fix this
    # Delete and recreate an existing matchup to rebuild result
    # - a sad hack rather than the effort of replacing the trigger
    matchup = MatchUp.query.filter_by(Match_ID=matchid).first()

    # If there's at least one matchup use it to trigger Result rebuild
    if matchup:
        # Build new MatchUp record
        newmatchup = MatchUp(OpponentName=matchup.OpponentName,
                             MyPlayerRank=matchup.MyPlayerRank,
                             OpponentRank=matchup.OpponentRank,
                             Player_ID=matchup.Player_ID,
                             MatchUpRace=matchup.MatchUpRace,
                             MyPlayerWire=matchup.MyPlayerWire,
                             MyPlayerScore=matchup.MyPlayerScore,
                             OpponentScore=matchup.OpponentScore,
                             Match_ID=matchup.Match_ID,
                             MyPlayerActual=matchup.MyPlayerActual,
                             OpponentActual=matchup.OpponentActual,
                             WinLose=matchup.WinLose)

        MatchUp.query.filter_by(idmatchup=matchup.idmatchup).delete()
        db.session.add(newmatchup)

    # If not, just delete the Result record
    else:
        Result.query.filter_by(Match_ID=matchid).delete()

    flash('Match Up deleted - ID : {}. Match ID {}'.format(matchupid, matchid))

    db.session.commit()

    return redirect(url_for('main.index'))


@bp.route('/matchover/<matchid>', methods=['GET', 'POST'])
@login_required
def matchover(matchid):
    if current_user.UserRole != 'Admin':
        return redirect(url_for('main.index'))

    m = Match.query.filter_by(idmatch=matchid).first()
    m.MatchOver = "Y"
    db.session.commit()
    flash('Match completed -  Match ID: {}'.format(matchid))
    return redirect(url_for('main.index'))

