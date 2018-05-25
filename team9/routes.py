from flask import render_template, flash, redirect
from team9 import team9, db
from team9.models import Player, Match
from team9.forms import LoginForm, AddMatch

# TODO Split routes into separate views (MVC)

@team9.route('/')
@team9.route('/index')
def index():
    season = {'seasonname' : 'Summer 2018'}
    players = Player.query.filter_by(Active='Y')
    return render_template('index.html', season=season, players=players)


@team9.route('/ranking')
def ranking():
    season = {'seasonname' : 'Summer 2018'}
    rankings = db.session.execute("SELECT * FROM AmsterdamTeam9.player_ranking").fetchall()
    return render_template('rank.html', season=season, rankings=rankings)


@team9.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(form.username.data, form.remember.data))
        return redirect('/index')
    return render_template('login.html', title='Make yourself known to me', form=form)


@team9.route('/addmatch', methods=['GET', 'POST'])
def addmatch():
    form = AddMatch()
    # Returns true on the POST when validation has passed
    if form.validate_on_submit():
        flash('Adding new match to the database for {}, against {}'.format(form.matchdate.data, form.opposingteam.data))
        return redirect('/index')
    # Renders on the GET of when the input does not validate
    return render_template('addmatch.html', title='Add Match', form=form)