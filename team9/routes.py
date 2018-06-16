from flask import render_template, flash, redirect, url_for
from team9 import team9, db, email
from team9.models import Player, Match, Season, MatchUp, User, Result
from team9.forms import LoginForm, AddMatch, AddMatchUp, RegistrationForm, BogMan, UserMan
from helper import hcaps
from flask_login import current_user, login_user, logout_user, login_required


# TODO Refactor project structure - Split routes into separate views (MVC)
# TODO Add Season Selector Form


# Get current season, which is used by the 'Add' forms
season = Season.query.filter_by(CurrentSeason='Y').first()


@team9.route('/')
@team9.route('/index')
def index():
    # TODO Create a splash page and separate from The Bog
    # TODO Fix Bog joins so that players appear when they have no matches played
    # TODO Revisit use of email - this is currently working as is - use for registration and weekly announcements
    # email.send_email('YRD', 'yourackdiscipline@gmail.com', ['paulecar@mac.com'], 'Hello', '<h1>HTML body</h1>')
    players =  db.session.execute("SELECT * FROM AmsterdamTeam9.the_bog").fetchall()
    nextmatch = Match.query.order_by(Match.MatchDate.desc()).first()
    return render_template('index.html', season=season.SeasonName, players=players, nextmatch=nextmatch)


@team9.route('/ranking')
def ranking():
    rankings_matchpct = db.session.execute\
        ("SELECT * FROM AmsterdamTeam9.player_ranking WHERE idseason = {} ORDER BY MatchPct Desc".format(season.idseason)).fetchall()
    rankings_rackspct = db.session.execute\
        ("SELECT * FROM AmsterdamTeam9.player_ranking WHERE idseason = {} ORDER BY RacksPct Desc".format(season.idseason)).fetchall()
    rankings_actpct = db.session.execute\
        ("SELECT * FROM AmsterdamTeam9.player_ranking WHERE idseason = {} ORDER BY ActPct Desc".format(season.idseason)).fetchall()
    return render_template('rank.html',
                           season=season.SeasonName,
                           rankings1=rankings_matchpct,
                           rankings2=rankings_rackspct,
                           rankings3=rankings_actpct)


@team9.route('/history')
@login_required
def history():
    if current_user.Player_ID is None:
        return redirect(url_for('index'))

    player = Player.query.filter_by(idplayer=current_user.Player_ID).first()
    player_history = db.session.execute\
        ("SELECT * FROM AmsterdamTeam9.player_history WHERE idplayer = {}".format(current_user.Player_ID)).fetchall()
    return render_template('history.html', history=player_history, player=player)


@team9.route('/results')
@login_required
def results():
    season_history = db.session.query(Result, Match).join(Match, Result.Match_ID == Match.idmatch).filter_by(Season_ID=9).order_by(Match.MatchDate.desc()).all()
    return render_template('season.html', history=season_history, season=season)


@team9.route('/matchresult/<matchid>')
@login_required
def matchresult(matchid):
    results = db.session.query(Player, MatchUp, Match).join(MatchUp, Player.idplayer == MatchUp.Player_ID).join(Match, Match.idmatch == MatchUp.Match_ID).filter_by(idmatch=matchid).all()
    return render_template('matchresult.html', results=results)

@team9.route('/userlist')
@login_required
def userlist():
    if current_user.UserRole != 'Admin':
        return redirect(url_for('index'))
    users = User.query.outerjoin(Player, Player.idplayer == User.Player_ID).\
        add_columns(User.id, User.UserName, User.Email, User.ConfCode, User.Verified, User.UserRole, Player.FirstName, Player.Surname).all()
    return render_template('userlist.html', userlist=users)


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
@login_required
def addmatch():
    if current_user.UserRole != 'Admin':
        return redirect(url_for('index'))
    form = AddMatch()

    # Pick list for opposing team
    i=0
    form.picks.append((0,'New Team..'))
    teams = db.session.query(Match.OpposingTeam).group_by(Match.OpposingTeam).\
        order_by(Match.OpposingTeam).all()
    for team in teams:
        i=i+1
        form.picks.append((i,team.OpposingTeam))

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
                          StartTime=form.starttime.data,
                          Season_ID=season.idseason,
                          PlayOff='Y')
        else:
            match = Match(OpposingTeam=team_entered,
                          MatchDate=form.matchdate.data,
                          StartTime=form.starttime.data,
                          Season_ID=season.idseason)
        db.session.add(match)
        db.session.commit()
        flash('Added new match on {}, against {}, where playoff is {}'.
              format(form.matchdate.data, team_entered, form.playoff.data))
        return redirect(url_for('index'))
    # Renders on the GET of when the input does not validate
    return render_template('addmatch.html', title='Add Match', form=form)


@team9.route('/addmatchup', methods=['GET', 'POST'])
@login_required
def addmatchup():
    if current_user.UserRole != 'Admin':
        return redirect(url_for('index'))
    form = AddMatchUp()

    # Matches from the current season
    season = Season.query.filter_by(CurrentSeason='Y').first()
    matches = Match.query.filter_by(Season_ID=season.idseason).order_by(Match.MatchDate.desc()).all()
    for m in matches:
        desc = m.OpposingTeam + ' on ' + str(m.MatchDate)
        form.match.append((m.idmatch, desc))


    # Our team - active players
    playernames = Player.query.filter_by(Active='Y').order_by(Player.Surname).all()
    for playername in playernames:
        form.player.append((playername.idplayer, playername.FirstName + ' ' + playername.Surname))


    # Opposing team players - from match up history (no join to opposing team data)
    i=0
    form.opponent.append((0, 'New Opponent...'))
    opponentnames = db.session.query(MatchUp.OpponentName).group_by(MatchUp.OpponentName).\
        order_by(MatchUp.OpponentName).all()
    for opponentname in opponentnames:
        i=i+1
        form.opponent.append((i, opponentname.OpponentName))


    # Racks to win - 0 thru 11 only
    i=0
    while i < 12:
        form.racks.append((i,i))
        i = i + 1


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
                          Match_ID=form.matchpick.data,
                          MyPlayerActual=form.playerscore.data - wire,
                          OpponentActual=form.opponentscore.data - oppwire,
                          WinLose=result)
        db.session.add(matchup)
        db.session.commit()
        flash('Added new match up : Player ID {} {} against {} {}'.
              format(form.playerpick.data, form.playerrank.data, opponent_entered, form.opponentrank.data))
        return redirect(url_for('index'))
    # Renders on the GET of when the input does not validate
    return render_template('addmatchup.html', title='Add Result', form=form, action='Create a New')


@team9.route('/deletematchup/<matchupid>/<matchid>', methods=['GET', 'POST'])
@login_required
def deletematchup(matchupid, matchid):
    if current_user.UserRole != 'Admin':
        return redirect(url_for('index'))

    MatchUp.query.filter_by(idmatchup=matchupid).delete()
    # TODO Revisit - deleting always requires an add to rebuild the result table
    Result.query.filter_by(Match_ID=matchid).delete()
    db.session.commit()
    flash('Match result deleted - add a new match up to rebuild results correctly')
    return redirect(url_for('index'))


@team9.route('/bogman', methods=['GET', 'POST'])
@login_required
def bogman():
    if current_user.UserRole != 'Admin':
        return redirect(url_for('index'))
    form = BogMan()

    # Our team - active players
    playernames = Player.query.filter_by(Active='Y').order_by(Player.Surname).all()
    for playername in playernames:
        form.player.append((playername.idplayer, playername.FirstName + ' ' + playername.Surname))


    if form.validate_on_submit():
        player = Player.query.filter_by(idplayer=form.playerpick.data).first()
        player.Bogged = form.bogged.data
        if form.change.data == 'Y':
            player.BoggedDate = form.bogdate.data
        db.session.commit()
        flash('Bogged data amended for Player {}, Bogged {}'.format(form.playerpick.data, form.bogged.data))
        return redirect(url_for('index'))
    # Renders on the GET of when the input does not validate
    return render_template('bogman.html', title='Bog Manager', form=form)


@team9.route('/userman', methods=['GET', 'POST'])
@login_required
def userman():
    if current_user.UserRole != 'Admin':
        return redirect(url_for('index'))
    form = UserMan()

    playernames = Player.query.filter_by(Active='Y').order_by(Player.Surname).all()
    for playername in playernames:
        form.player.append((playername.idplayer, playername.FirstName + ' ' + playername.Surname))


    users = User.query.order_by(User.UserName).all()
    for userid in users:
        form.user.append((userid.id, userid.UserName + ' ' + userid.Email))


    if form.validate_on_submit():
        user = User.query.filter_by(id=form.userpick.data).first()
        user.Player_ID = form.playerpick.data
        db.session.commit()
        flash('Player ID set for User {}, Player {}'.format(form.userpick.data, form.playerpick.data))
        return redirect(url_for('index'))
    # Renders on the GET of when the input does not validate
    return render_template('userman.html', title='User Manager', form=form)

