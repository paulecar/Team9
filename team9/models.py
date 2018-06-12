from team9 import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Player(db.Model):
    __table__ = db.Model.metadata.tables['Player']

    def __repr__(self):
        return self.Surname


class Match(db.Model):
    __table__ = db.Model.metadata.tables['Match']

    def __repr__(self):
        return self.idmatch


class MatchUp(db.Model):
    __table__ = db.Model.metadata.tables['MatchUp']

    def __repr__(self):
        return self.idmatchup


class Season(db.Model):
    __table__ = db.Model.metadata.tables['Season']

    def __repr__(self):
        return self.SeasonName


class Result(db.Model):
    __table__ = db.Model.metadata.tables['Result']

    def __repr__(self):
        return self.idresult


class User(UserMixin, db.Model):
    __table__ = db.Model.metadata.tables['User']

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