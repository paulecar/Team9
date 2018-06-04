from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError, InputRequired, Required, Length

# TODO Session expiration so new team is immediately available in the pick list
# I think there are multiple session objects,
# so I need a sessionmaker in __init__.py
# Docs at http://docs.sqlalchemy.org/en/latest/orm/session_state_management.html


# Database Items
from team9 import db
from team9.models import Match, MatchUp, Player

from datetime import datetime
from helper import hcaps, ranks

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class AddMatch(FlaskForm):
    # TODO Add match start time
    i=0
    picks=[]
    picks.append((0,'New Team..'))
    teams = db.session.query(Match.OpposingTeam).group_by(Match.OpposingTeam).\
        order_by(Match.OpposingTeam).all()
    for team in teams:
        i=i+1
        picks.append((i,team.OpposingTeam))
    teampick = SelectField('Pick Team', choices=picks, coerce=int)
    opposingteam = StringField('Opposing Team')
    playoff = BooleanField('Playoff Match')
    # TODO Revisit 'flask-moment' extension from 'Dates and Times' section
    matchdate = DateField('Match Date', validators=[DateField], default=datetime.today() , format="%Y-%m-%d")
    submit = SubmitField('Create Match')


    def validate_opposingteam(self, opposingteam):
        # TODO Is there a more elegant way to address this option
        # 0 means 'New team..'
        if self.teampick.data==0:
            if len(self.opposingteam.data)==0:
                raise ValidationError('Select Opposing Team from list or Enter a team name in the text box.')

class AddMatchUp(FlaskForm):
    # Create pick lists
    # Our team - active players
    player=[]
    playernames = Player.query.filter_by(Active='Y').order_by(Player.Surname).all()
    for playername in playernames:
        player.append((playername.idplayer, playername.Surname))


    # Opposing team players - from match up history (no join to opposing team data)
    i=0
    opponent=[]
    opponent.append((0, 'New Opponent...'))
    opponentnames = db.session.query(MatchUp.OpponentName).group_by(MatchUp.OpponentName).\
        order_by(MatchUp.OpponentName).all()
    for opponentname in opponentnames:
        i=i+1
        opponent.append((i, opponentname.OpponentName))

    # Racks to win - 0 thru 11 only
    i=0
    racks=[]
    while i < 12:
        racks.append((i,i))
        i = i + 1


    # Main from starts here
    playerpick = SelectField('Select Our Player',
                             choices=player, coerce=int)
    playerrank = SelectField('Select Player Rank', choices=ranks)
    opponentpick = SelectField('Select Opponent  or enter New Player',
                               choices=opponent, coerce=int)
    opponentname = StringField('Opponent')
    opponentrank = SelectField('Select Opponent Rank', choices=ranks)
    playerscore = SelectField('Our Player Scores', choices=racks, coerce=int)
    opponentscore = SelectField('Opponent Scores', choices=racks, coerce=int)
    mathematical_elimination = BooleanField('Mathematical elimination stops play')
    submit = SubmitField('Create Match')


    def validate_opponentname(self, opponentname):
        # 0 means 'New Opponent..'
        if self.opponentpick.data==0:
            if len(self.opponentname.data)==0:
                raise ValidationError('Select Opponent from list or Enter a name in the text box.')

    def validate_playerscore(self, playerscore):
        try:
            race = hcaps[self.playerrank.data][self.opponentrank.data]
        except:
            raise ValidationError('Something went wrong with race lookup (player)?')

        if self.playerscore.data < race[0]:
            raise ValidationError('Player score appears to be less than racks given on the wire?')

        if self.playerscore.data > race[1]:
            raise ValidationError('Player score appears to be more than required number of racks')

        # TODO Tidy up this validation to remove duplicate code
        if self.opponentscore.data < race[1]\
                and self.playerscore.data < race[1] \
                and not self.mathematical_elimination.data:
            raise ValidationError('One of the players must reach the target number of racks : ' + race[1].__str__())


    def validate_opponentscore(self, opponentscore):
        try:
            race = hcaps[self.playerrank.data][self.opponentrank.data]
        except:
            raise ValidationError('Something went wrong with race lookup (opponent)?')

        if self.opponentscore.data < (race[0] * -1):
            raise ValidationError('Opponent score appears to be less than racks given on the wire?')

        if self.opponentscore.data > race[1]:
            raise ValidationError('Opponent score appears to be more than required number of racks')

        if self.opponentscore.data < race[1]\
                and self.playerscore.data < race[1] \
                and not self.mathematical_elimination.data:
            raise ValidationError('One of the players must reach the target number of racks : ' + race[1].__str__())
