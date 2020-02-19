from flask import current_app, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from team9 import db
from team9.email import bp, email
from team9.email.forms import Message
from team9.models import Player, User, Match
from team9utils import kvmSet, kvmGet


@bp.route('/message', methods=['GET', 'POST'])
@login_required
def message():
    if current_user.UserRole != 'Admin':
        return redirect(url_for('main.index'))

    form=Message()
    current_message = kvmGet('CAPTAINSMESSAGE')

    if form.validate_on_submit():
        kvmSet('CAPTAINSMESSAGE', form.weekly_message.data)
        flash('Email message set : {}'.format(form.weekly_message.data))
        return redirect(url_for('main.index'))

    return render_template('email/message.html', title='Update Email Message', form=form, current_message=current_message)


@bp.route('/sendemail')
@login_required
def sendemail():
    # All players with a linked user - outer join means we can have 'None' for a User
    players = db.session.query(Player, User).outerjoin(User, User.Player_ID == Player.idplayer).order_by(Player.Surname.asc()).all()

    # Nextmatch - speaks for itself
    nextmatch = Match.query.order_by(Match.MatchDate.asc(), Match.StartTime.asc()).\
        filter(Match.MatchOver == None).first()

    cclist = []
    lineup = []
    # Walk through the Players and create email cc list and line-up for the text email (only)
    for player in players:
        if player.Player.Active == "Y":
            if player.User:
                if player.User.Email:
                    cclist.append(player.User.Email)
            if player.Player.Bogged == 'N':
                lineup.append(player.Player.FirstName + " " + player.Player.Surname)

    # The email body for recipients with non-HTML email clients.
    text_body = ("The next match is on " + "{:%A, %d %b }".format(nextmatch.MatchDate) +
                 " @ " + "{:%H:%M}".format(nextmatch.StartTime) +
                 " versus " + nextmatch.OpposingTeam + "\r\n" +
                 "The Rule of the Bog is in full stench, and our line up is: " + ", ".join(lineup) + "\r\n\n" +
                 "Please CONFIRM that you are able to attend.")

    image_file = kvmGet('LATESTPICTURE')
    # cid = "cid:" + current_app.config['STATIC_FILES'] + "/" + image_file

    email.send_image_email(cclist, text_body,
                           render_template('email/image_email.html',
                                           players=players,
                                           nextmatch=nextmatch,
                                           captainsMessage=kvmGet('CAPTAINSMESSAGE'),
                                           image=image_file))

    # email.send_mime_email(cclist, text_body, image_file,
    #                       render_template('email/mime_email.html',
    #                                       players=players,
    #                                       nextmatch=nextmatch,
    #                                       captainsMessage=kvmGet('CAPTAINSMESSAGE'),
    #                                       cid=cid,
    #                                       image=image_file))

    return redirect(url_for('main.index'))

