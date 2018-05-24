from team9 import db

class Player(db.Model):
    __table__ = db.Model.metadata.tables['Player']

    def __repr__(self):
        return self.Surname


class Match(db.Model):
    __table__ = db.Model.metadata.tables['Match']

    def __repr__(self):
        return self.idMatch

# TODO Revisit relecting the views - problem was linked to the lack of a primary key
# class Rankings(db.Model):
#    __table__ = db.Model.metadata.views['playerranking']
#
#    def __repr__(self):
#        return self.Player_ID