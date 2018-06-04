from flask import render_template, flash, redirect, url_for
from team9 import team9, db
from team9.models import Player, Match, Season, MatchUp
from team9.forms import LoginForm, AddMatch, AddMatchUp
from helper import hcaps


# TODO Split routes into separate views (MVC)


# Get current season, which is used by the 'Add' forms
season = Season.query.filter_by(CurrentSeason='Y').first()


@team9.route('/')
@team9.route('/index')
def index():
    # TODO Create a nicer splash page - Player list with most recent ranking
    season = {'seasonname' : 'Summer 2018'}
    players = Player.query.filter_by(Active='Y').order_by(Player.idplayer)
    return render_template('index.html', season=season, players=players)


@team9.route('/ranking')
def ranking():
    # TODO Make ranking table more dynamic - pick a season
    season = {'seasonname' : 'Summer 2018'}
    rankings_matchpct = db.session.execute\
        ("SELECT * FROM AmsterdamTeam9.player_ranking WHERE idseason = 8 ORDER BY MatchPct Desc").fetchall()
    rankings_rackspct = db.session.execute\
        ("SELECT * FROM AmsterdamTeam9.player_ranking WHERE idseason = 8 ORDER BY RacksPct Desc").fetchall()
    rankings_actpct = db.session.execute\
        ("SELECT * FROM AmsterdamTeam9.player_ranking WHERE idseason = 8 ORDER BY ActPct Desc").fetchall()
    return render_template('rank.html',
                           season=season,
                           rankings1=rankings_matchpct,
                           rankings2=rankings_rackspct,
                           rankings3=rankings_actpct)


@team9.route('/login', methods=['GET', 'POST'])
def login():
    # TODO Enable user login page (defer registration for later)
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, '
              'remember_me={}'.format(form.username.data, form.remember.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@team9.route('/addmatch', methods=['GET', 'POST'])
def addmatch():
    form = AddMatch()
    if form.validate_on_submit():
        # If 'New Team' selected then use the form input field,
        # otherwise the value from selected tuple
        if form.teampick.data==0:
            team_entered = form.opposingteam.data
        else:
            team_entered = form.teampick.choices[form.teampick.data][1]
        if form.playoff.data:
            match = Match(OpposingTeam=team_entered,
                          MatchDate=form.matchdate.data,
                          Season_ID=season.idseason,
                          PlayOff='Y')
        else:
            match = Match(OpposingTeam=team_entered,
                          MatchDate=form.matchdate.data,
                          Season_ID=season.idseason)
        db.session.add(match)
        db.session.commit()
        flash('Added new match on {}, against {}, where playoff is {}'.
              format(form.matchdate.data, team_entered, form.playoff.data))
        return redirect(url_for('index'))
    # Renders on the GET of when the input does not validate
    return render_template('addmatch.html', title='Add Match', form=form)

@team9.route('/addmatchup', methods=['GET', 'POST'])
def addmatchup():
    # Get the current Match
    current_match = Match.query.order_by(Match.MatchDate.desc()).first()
    form = AddMatchUp()
    if form.validate_on_submit():
        # If 'New Player' selected then use the form input field,
        # otherwise the value from selected tuple
        if form.opponentpick.data==0:
            opponent_entered = form.opponentname.data
        else:
            opponent_entered = form.opponentpick.choices[form.opponentpick.data][1]
        race = hcaps[form.playerrank.data][form.opponentrank.data]
        if race[0] < 0:
            wire = 0
            oppwire = race[0] * -1
        else:
            wire = race[0]
            oppwire = 0
        if form.playerscore.data > form.opponentscore.data:
            result='W'
        else:
            result='L'
        matchup = MatchUp(OpponentName=opponent_entered,
                          MyPlayerRank=form.playerrank.data,
                          OpponentRank=form.opponentrank.data,
                          Player_ID=form.playerpick.data,
                          MatchUpRace=race[1],
                          MyPlayerWire=race[0],
                          MyPlayerScore=form.playerscore.data,
                          OpponentScore=form.opponentscore.data,
                          Match_ID=current_match.idmatch,
                          MyPlayerActual=form.playerscore.data - wire,
                          OpponentActual=form.opponentscore.data - oppwire,
                          WinLose=result)
        db.session.add(matchup)
        db.session.commit()
        flash('Added new match up : Player ID {} {} against {} {}'.
              format(form.playerpick.data, form.playerrank.data, opponent_entered, form.opponentrank.data))
        return redirect(url_for('index'))
    # Renders on the GET of when the input does not validate
    return render_template('addmatchup.html', title='Add MatchUp', form=form, cm=current_match)