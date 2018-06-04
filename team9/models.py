from team9 import db

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


class Bog(db.Model):
    __table__ = db.Model.metadata.tables['Bog']

    def __repr__(self):
        return self.idbogentry


# TODO Revisit reflecting the views - problem was linked to the lack of a primary key
# class Rankings(db.Model):
#    __table__ = db.Model.metadata.views['playerranking']
#
#    def __repr__(self):
#        return self.Player_ID