from flask import render_template, flash, redirect, url_for
from team9 import team9, db
from team9.models import Player, Match, Season, MatchUp, User
from team9.forms import LoginForm, AddMatch, AddMatchUp, RegistrationForm, BogMan
from helper import hcaps
from flask_login import current_user, login_user, logout_user


# TODO Refactor project structure - Split routes into separate views (MVC)

# TODO Add Season Selector Form
# TODO Add Bog Manager Form


# Get current season, which is used by the 'Add' forms
season = Season.query.filter_by(CurrentSeason='Y').first()


@team9.route('/')
@team9.route('/index')
def index():
    # TODO Create a splash page and separate from The Bog
    # TODO Fix Bog joins so that players appear when they have no matches played
    seasonname = {'seasonname' : season.SeasonName}
    players =  db.session.execute("SELECT * FROM AmsterdamTeam9.the_bog").fetchall()
    return render_template('index.html', season=seasonname, players=players)


@team9.route('/ranking')
def ranking():
    seasonname = {'seasonname' : season.SeasonName}
    rankings_matchpct = db.session.execute\
        ("SELECT * FROM AmsterdamTeam9.player_ranking WHERE idseason = {} ORDER BY MatchPct Desc".format(season.idseason)).fetchall()
    rankings_rackspct = db.session.execute\
        ("SELECT * FROM AmsterdamTeam9.player_ranking WHERE idseason = {} ORDER BY RacksPct Desc".format(season.idseason)).fetchall()
    rankings_actpct = db.session.execute\
        ("SELECT * FROM AmsterdamTeam9.player_ranking WHERE idseason = {} ORDER BY ActPct Desc".format(season.idseason)).fetchall()
    return render_template('rank.html',
                           season=seasonname,
                           rankings1=rankings_matchpct,
                           rankings2=rankings_rackspct,
                           rankings3=rankings_actpct)


@team9.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(UserName=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@team9.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@team9.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(UserName=form.username.data, Email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


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

@team9.route('/bogman', methods=['GET', 'POST'])
def bogman():
    form = BogMan()
    if form.validate_on_submit():
        player = Player.query.filter_by(idplayer=form.playerpick.data).first()
        player.Bogged = form.bogged.data
        player.BoggedDate = form.bogdate.data
        db.session.commit()
        flash('Bogged data amended for Player {}, Bogged {}'.format(form.playerpick.data, form.bogged.data))
        return redirect(url_for('index'))
    # Renders on the GET of when the input does not validate
    return render_template('bogman.html', title='Bog Manager', form=form)

