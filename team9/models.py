from team9 import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Player(db.Model):
    __table__ = db.Model.metadata.tables['player']

    def __repr__(self):
        return self.Surname


class Match(db.Model):
    __table__ = db.Model.metadata.tables['match']

    def __repr__(self):
        return self.OpposingTeam


class MatchUp(db.Model):
    __table__ = db.Model.metadata.tables['matchup']

    def __repr__(self):
        return self.OpponentName


class Season(db.Model):
    __table__ = db.Model.metadata.tables['season']

    def __repr__(self):
        return self.SeasonName


class Result(db.Model):
    __table__ = db.Model.metadata.tables['result']

    def __repr__(self):
        return str(self.idresult)


class User(UserMixin, db.Model):
    __table__ = db.Model.metadata.tables['user']

    def __repr__(self):
        return self.UserName

    def set_password(self, Password):
        self.PasswordHash = generate_password_hash(Password)

    def check_password(self, Password):
        return check_password_hash(self.PasswordHash, Password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


# TODO Revisit reflecting the views - problem was linked to the lack of a primary key
# class Rankings(db.Model):
#    __table__ = db.Model.metadata.views['playerranking']
#
#    def __repr__(self):
#        return self.Player_ID
