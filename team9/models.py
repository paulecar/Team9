from team9 import db

class Player(db.Model):
    __table__ = db.Model.metadata.tables['Player']

    def __repr__(self):
        return self.Surname

# class Rankings(db.Model):
#    __table__ = db.Model.metadata.views['playerranking']
#
#    def __repr__(self):
#        return self.Player_ID