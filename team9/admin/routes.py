from flask import current_app, render_template, flash, redirect, url_for, request
from team9 import db
from team9.models import Player, Match, Season, MatchUp, User, Result, Availability
from team9.admin.forms import AddMatch, AddSeason, AddPlayer, \
    AddMatchUp, UploadForm, SeasonMan, BogMan, UserMan, UpdateMatch
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import os
from team9.admin import bp
from team9utils import getRace, setWinner, allowed_file, kvmSet, kvmGet


@bp.route('/addmatch', methods=['GET', 'POST'])
@login_required
def addmatch():
    if current_user.UserRole != 'Admin':
        return redirect(url_for('main.index'))
    form = AddMatch()

    # Pick list for opposing team
    i = 0
    form.picks.clear()
    form.picks.append((0, 'New Team..'))
    teams = db.session.query(Match.OpposingTeam).group_by(Match.OpposingTeam). \
        order_by(Match.OpposingTeam).all()
    for team in teams:
        i = i + 1
        form.picks.append((i, team.OpposingTeam))

    if form.validate_on_submit():
        # Get current season
        season = Season.query.filter_by(CurrentSeason='Y').first()

        # If 'New Team' selected then use the form input field,
        # otherwise the value from selected tuple
        if form.teampick.data == 0:
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
        return redirect(url_for('main.index'))
    # Renders on the GET or when the input does not validate
    return render_template('admin/addmatch.html', title='Add Match', form=form)


@bp.route('/addmatchup/<matchid>', methods=['GET', 'POST'])
@login_required
def addmatchup(matchid):
    if current_user.UserRole != 'Admin' and current_user.UserRole != 'Helper':
        return redirect(url_for('main.index'))
    form = AddMatchUp()

    match = Match.query.filter_by(idmatch=matchid).first()
    desc = match.OpposingTeam + ' on ' + str(match.MatchDate)

    # Our team - active players
    playernames = Player.query.filter_by(Active='Y').order_by(Player.Surname).all()
    form.player.clear()
    for playername in playernames:
        form.player.append((playername.idplayer, playername.FirstName + ' ' + playername.Surname))

    # Opposing team players - from match up history (no join to opposing team data)
    i = 0
    form.opponent.clear()
    form.opponent.append((0, 'New Opponent...'))
    opponentnames = db.session.query(MatchUp.OpponentName).group_by(MatchUp.OpponentName). \
        order_by(MatchUp.OpponentName).all()
    for opponentname in opponentnames:
        i = i + 1
        form.opponent.append((i, opponentname.OpponentName))

    if form.validate_on_submit():
        # If 'New Player' selected then use the form input field,
        # otherwise the value from selected tuple
        if form.opponentpick.data == 0:
            opponent_entered = form.opponentname.data
        else:
            opponent_entered = form.opponentpick.choices[form.opponentpick.data][1]

        # Get race details so we can calculate 'actual' racks won/lost, etc.
        wire, oppwire, race = getRace(form.playerrank.data, form.opponentrank.data)

        result = setWinner(race, form.playerscore.data,
                           form.opponentscore.data,
                           form.mathematical_elimination.data)

        # Store the data in new MatchUp record
        matchup = MatchUp(OpponentName=opponent_entered,
                          MyPlayerRank=form.playerrank.data,
                          OpponentRank=form.opponentrank.data,
                          Player_ID=form.playerpick.data,
                          MatchUpRace=race[1],
                          MyPlayerWire=race[0],
                          MyPlayerScore=form.playerscore.data,
                          OpponentScore=form.opponentscore.data,
                          Match_ID=match.idmatch,
                          MyPlayerActual=form.playerscore.data - wire,
                          OpponentActual=form.opponentscore.data - oppwire,
                          WinLose=result)

        db.session.add(matchup)
        db.session.commit()

        flash('Added new match up : Player {} ({}) against {} ({})'.
              format(dict(form.player)[form.playerpick.data], form.playerrank.data, opponent_entered, form.opponentrank.data))

        return redirect(url_for('main.index'))

    # Renders on the GET or when the input does not validate
    return render_template('admin/addmatchup.html', title='Add Result', form=form, action='Create',
                           opposing_team=desc)


@bp.route('/addplayer', methods=['GET', 'POST'])
@login_required
def addplayer():
    if current_user.UserRole != 'Admin':
        return redirect(url_for('main.index'))
    form = AddPlayer()

    if form.validate_on_submit():
        newplayer = Player(Surname=form.surname.data,
                      FirstName=form.firstname.data,
                      Bogged='N',
                      Active='Y')
        db.session.add(newplayer)
        db.session.commit()
        flash('Added new player {} {}'.format(newplayer.FirstName, newplayer.Surname))
        return redirect(url_for('main.index'))
    # Renders on the GET of when the input does not validate
    return render_template('admin/addplayer.html', title='Add Player', form=form)


@bp.route('/addseason', methods=['GET', 'POST'])
@login_required
def addseason():
    if current_user.UserRole != 'Admin':
        return redirect(url_for('main.index'))
    form = AddSeason()

    if form.validate_on_submit():
        newseason = Season(SeasonName=form.seasonname.data,
                      SeasonStart=form.startdate.data,
                      SeasonEnd=form.enddate.data,
                      CurrentSeason=form.current.data)
        db.session.add(newseason)
        db.session.commit()
        flash('Added new season {}, Starting : {} - Ending : {}'.
              format(newseason.SeasonName, newseason.SeasonStart, newseason.SeasonEnd))
        return redirect(url_for('main.index'))
    # Renders on the GET of when the input does not validate
    return render_template('admin/addseason.html', title='Add Season', form=form)


@bp.route('/bogger/<playerid>', methods=['GET', 'POST'])
@login_required
def bogger(playerid):
    if current_user.UserRole != 'Admin':
        return redirect(url_for('main.index'))

    player = Player.query.filter_by(idplayer=playerid).first()

    if player.Bogged == "Y":
        player.Bogged = "N"
        flash('Player {} {} - UnBogged'.format(player.FirstName, player.Surname))
    else:
        player.Bogged = "Y"
        flash('Player {} {} - Bogged'.format(player.FirstName, player.Surname))

    db.session.commit()
    return redirect(url_for('main.index'))


@bp.route('/bogman/<playerid>', methods=['GET', 'POST'])
@login_required
def bogman(playerid):
    if current_user.UserRole != 'Admin':
        return redirect(url_for('main.index'))

    player = Player.query.filter_by(idplayer=playerid).first()
    playername = player.FirstName + ' ' + player.Surname

    if player.BoggedDate:
        form = BogMan(bogged=player.Bogged, active=player.Active, bogdate=player.BoggedDate)
    else:
        form = BogMan(bogged=player.Bogged, active=player.Active)

    if form.validate_on_submit():
        player.Bogged = form.bogged.data
        player.Active = form.active.data

        if form.change.data == 'Y':
            player.BoggedDate = form.bogdate.data
        db.session.commit()
        flash('Player data amended for : {} {} - Bogged : {} - Active : {}'.format(player.FirstName, player.Surname, player.Bogged, player.Active))
        return redirect(url_for('main.index'))
    # Renders on the GET or when the input does not validate
    return render_template('admin/bogman.html', title='Bog Manager', form=form, player=playername)


@bp.route('/deletematch/<matchid>', methods=['GET', 'POST'])
@login_required
def deletematch(matchid):
    if current_user.UserRole != 'Admin':
        return redirect(url_for('main.index'))

    Availability.query.filter_by(Match_ID=matchid).delete()
    Result.query.filter_by(Match_ID=matchid).delete()
    MatchUp.query.filter_by(Match_ID=matchid).delete()
    Match.query.filter_by(idmatch=matchid).delete()
    db.session.commit()
    flash('Match record and related results deleted for Match ID {}'.format(matchid))
    return redirect(url_for('main.results'))


@bp.route('/deleteuser/<userid>', methods=['GET', 'POST'])
@login_required
def deleteuser(userid):
    if current_user.UserRole != 'Admin':
        return redirect(url_for('main.index'))

    User.query.filter_by(id=userid).delete()
    db.session.commit()
    flash('User deleted with ID {}'.format(userid))
    return redirect(url_for('main.index'))


@bp.route('/seasonlist')
@login_required
def seasonlist():
    if current_user.UserRole != 'Admin':
        return redirect(url_for('main.index'))
    seasons = Season.query.order_by(Season.SeasonStart.desc()).all()
    return render_template('admin/seasonlist.html', seasons=seasons)


@bp.route('/seasonman/<id>', methods=['GET', 'POST'])
@login_required
def seasonman(id):
    if current_user.UserRole != 'Admin':
        return redirect(url_for('main.index'))
    season = Season.query.filter_by(idseason=id).first()
    form = SeasonMan(seasonname=season.SeasonName, startdate=season.SeasonStart,
                     enddate=season.SeasonEnd, current=season.CurrentSeason)

    if form.validate_on_submit():
        season.SeasonName = form.seasonname.data
        season.SeasonStart = form.startdate.data
        season.SeasonEnd = form.enddate.data
        season.CurrentSeason = form.current.data

        db.session.commit()
        flash('Restart may be required - Season data amended for : {} - StartDate/EndDate : {} {} - Current : {}'.
              format(season.SeasonName, "{:%A, %d %b, %Y }".format(season.SeasonStart),
                     "{:%A, %d %b, %Y }".format(season.SeasonEnd), season.CurrentSeason))
        return redirect(url_for('admin.seasonlist'))
    # Renders on the GET or when the input does not validate
    return render_template('admin/seasonman.html', title='Season Update', form=form, season=season.SeasonName)


@bp.route('/updatematch/<matchid>', methods=['GET', 'POST'])
@login_required
def updatematch(matchid):
    if current_user.UserRole != 'Admin':
        return redirect(url_for('main.index'))

    # Get match and pre-populate values
    match = Match.query.filter_by(idmatch=matchid).first()
    playoff_val = False
    if match.PlayOff == "Y":
        playoff_val = True

    form = UpdateMatch(matchdate=match.MatchDate, starttime=match.StartTime, playoff=playoff_val, opposingteam=match.OpposingTeam)

    if form.validate_on_submit():
        match = Match.query.filter_by(idmatch=matchid).first()

        match.OpposingTeam = form.opposingteam.data
        match.MatchDate = form.matchdate.data
        match.StartTime = form.starttime.data
        if form.playoff.data:
            match.PlayOff = "Y"
        else:
            match.PlayOff = None

        db.session.commit()
        flash('Match {} against {} changed.'.format(match.idmatch, match.OpposingTeam))
        return redirect(url_for('main.results'))
    # Renders on the GET or when the input does not validate
    return render_template('admin/updatematch.html', title='Update Match', form=form, )


@bp.route('/upload')
@login_required
def upload():
    if current_user.UserRole != 'Admin':
        return redirect(url_for('main.index'))

    form=UploadForm()
    image_file = kvmGet('LATESTPICTURE')

    return render_template('admin/upload.html', title='Upload JPG', form=form, image=image_file)


@bp.route('/uploader', methods=['GET', 'POST'])
@login_required
def uploader():
    if current_user.UserRole != 'Admin':
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('main.index'))

        f = request.files['file']

        if f.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if not allowed_file(f.filename):
            flash('Invalid file type')
            return redirect(url_for('main.index'))

        # Valid file type uploaded to directory that matches the users cookie ID value (uuid)
        os.makedirs(os.path.join(current_app.config['UPLOAD_FOLDER']), exist_ok=True)
        filename = secure_filename(f.filename)
        f.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        os.system("cp " + os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                 + " " + os.path.join(current_app.config['STATIC_FILES'], filename))

        kvmSet('LATESTPICTURE', filename)
        flash('File uploaded successfully')

        return redirect(url_for('main.index'))


@bp.route('/userlist')
@login_required
def userlist():
    if current_user.UserRole != 'Admin':
        return redirect(url_for('main.index'))
    users = User.query.outerjoin(Player, Player.idplayer == User.Player_ID). \
        add_columns(User.id, User.UserName, User.Email, User.ConfCode, User.Verified, User.UserRole, User.last_seen,
                    Player.FirstName, Player.Surname).order_by(User.UserName).all()
    return render_template('admin/userlist.html', userlist=users)


@bp.route('/userman/<id>', methods=['GET', 'POST'])
@login_required
def userman(id):
    if current_user.UserRole != 'Admin':
        return redirect(url_for('main.index'))

    playernames = Player.query.filter_by(Active='Y').order_by(Player.Surname).all()

    user = User.query.filter_by(id=id).first()
    user_id = str(user.id) + " : " + user.UserName + " (" + user.Email + ")"

    form = UserMan(userrole=user.UserRole, playerpick=user.Player_ID)
    form.player.clear()
    form.player.append((0, "Unlink"))
    for playername in playernames:
        form.player.append((playername.idplayer, playername.FirstName + ' ' + playername.Surname))


    if form.validate_on_submit():
        if form.playerpick.data == 0:
            user.Player_ID = None
        else:
            user.Player_ID = form.playerpick.data
        if form.userrole.data == "None":
            user.UserRole = None
        else:
            user.UserRole = form.userrole.data
        db.session.commit()
        flash('Player ID set for User : {} - Player : {} - Role : {}'.format(user_id, dict(form.player)[form.playerpick.data], user.UserRole))
        return redirect(url_for('admin.userlist'))
    # Renders on the GET of when the input does not validate
    return render_template('admin/userman.html', title='User Manager', form=form, user=user_id)
