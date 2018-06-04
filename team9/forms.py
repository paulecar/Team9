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
from handicaps import hcaps

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
    player=[]
    playernames = Player.query.filter_by(Active='Y').order_by(Player.Surname).all()
    for playername in playernames:
        player.append((playername.idplayer, playername.Surname))
    i=0
    opponent=[]
    opponent.append((0, 'New Opponent...'))
    opponentnames = db.session.query(MatchUp.OpponentName).group_by(MatchUp.OpponentName).\
        order_by(MatchUp.OpponentName).all()
    for opponentname in opponentnames:
        i=i+1
        opponent.append((i, opponentname.OpponentName))
    i=0
    racks=[]
    while i < 12:
        racks.append((i,i))
        i = i + 1
    # Main from starts here
    playerpick = SelectField('Select Our Player',
                             choices=player, coerce=int)
    # TODO Make player rank a pick list, or add validation
    playerrank = StringField('Player Rank',
                             validators=[Length(min=1, max=2,
                                    message='Player Rank is 1 or 2 chars only')])
    opponentpick = SelectField('Select Opponent  or enter New Player',
                               choices=opponent, coerce=int)
    opponentname = StringField('Opponent')
    opponentrank = StringField('Opponent Rank',
                               validators=[DataRequired(),
                               Length(min=1, max=2,
                                      message='Player Rank is 1 or 2 chars only')])
    playerscore = SelectField('Our Player Scores', choices=racks, coerce=int)
    opponentscore = SelectField('Opponent Scores', choices=racks, coerce=int)
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
            raise ValidationError('Ranks not set - cannot validate score')
        if self.playerscore.data < race[0]:
            raise ValidationError('Player score appears to be less than racks given on the wire?')

    def validate_opponentscore(self, opponentscore):
        try:
            race = hcaps[self.playerrank.data][self.opponentrank.data]
        except:
            raise ValidationError('Player score appears to be less than racks given on the wire?')
        if self.opponentscore.data < (race[0] * -1):
            raise ValidationError('Opponent score appears to be less than racks given on the wire?')

