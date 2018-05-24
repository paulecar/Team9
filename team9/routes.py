from flask import render_template
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
    rankings = db.session.execute("SELECT * FROM AmsterdamTeam9.playerranking").fetchall()
    return render_template('rank.html', season=season, rankings=rankings)


@team9.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', title='Make yourself known to me', form=form)


@team9.route('/addmatch')
def addmatch():
    form = AddMatch()
    return render_template('addmatch.html', title='Add Match', form=form)