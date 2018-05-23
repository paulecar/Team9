from flask import render_template
from team9 import team9, db
from team9.models import Player

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
