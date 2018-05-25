from team9 import db

class Player(db.Model):
    __table__ = db.Model.metadata.tables['Player']

    def __repr__(self):
        return self.Surname


class Match(db.Model):
    __table__ = db.Model.metadata.tables['Match']

    def __repr__(self):
        return self.idMatch

# TODO Introduce model for MathUp table

# TODO Introduce model for Season Table

# TODO Introduce model for Result table

# TODO Introduce model for 'HandicapRace' table

# TODO Introduce model for Bog table


# TODO Revisit relecting the views - problem was linked to the lack of a primary key
# class Rankings(db.Model):
#    __table__ = db.Model.metadata.views['playerranking']
#
#    def __repr__(self):
#        return self.Player_ID