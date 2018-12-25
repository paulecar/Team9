from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from team9 import db, login
from time import time
import jwt

class KeyValueMap(db.Model):
    __table__ = db.Model.metadata.tables['kvm']

    def __repr__(self):
        return self.key


class Availability(db.Model):
    __table__ = db.Model.metadata.tables['availability']

    def __repr__(self):
        return ("ID:" + str(self.idavailability) + ", Player:" + str(self.Player_ID) + ", Match:" + str(self.Match_ID))


class Player(db.Model):
    __table__ = db.Model.metadata.tables['player']

    def __repr__(self):
        return self.Surname


class Match(db.Model):
    __table__ = db.Model.metadata.tables['match']

    def __repr__(self):
        return ("ID:" + str(self.idmatch) + ", Team:" + self.OpposingTeam)


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

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


# TODO Revisit reflecting the views - problem was linked to the lack of a primary key
# class Rankings(db.Model):
#    __table__ = db.Model.metadata.views['playerranking']
#
#    def __repr__(self):
#        return self.Player_ID
