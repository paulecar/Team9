from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SelectField, BooleanField, SubmitField, RadioField
from wtforms_components import TimeField
from wtforms.validators import DataRequired, Email, ValidationError, InputRequired, Required, EqualTo


# TODO Session expiration so new team and new match date are immediately available in the pick list for addmatch
# I think there are multiple session objects,
# so I need a sessionmaker in __init__.py
# Docs at http://docs.sqlalchemy.org/en/latest/orm/session_state_management.html


# Database Items
from team9 import db
from team9.models import Match, MatchUp, Player, User, Season


from datetime import datetime
from helper import hcaps, ranks


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class AddMatch(FlaskForm):
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
    playoff = BooleanField('Playoff Match', default=False)
    # TODO Revisit 'flask-moment' extension from 'Dates and Times' section
    matchdate = DateField('Match Date', validators=[DateField], default=datetime.today(), format="%Y-%m-%d")
    starttime = TimeField('Start Time', validators=[TimeField])
    submit = SubmitField('Create Match')


    def validate_opposingteam(self, opposingteam):
        # 0 means 'New team..'
        if self.teampick.data==0:
            if len(self.opposingteam.data)==0:
                raise ValidationError('Select Opposing Team from list or Enter a team name in the text box.')


class AddMatchUp(FlaskForm):
    # Matches from the current season
    season = Season.query.filter_by(CurrentSeason='Y').first()
    match=[]
    matches = Match.query.filter_by(Season_ID=season.idseason).order_by(Match.MatchDate.desc()).all()
    for m in matches:
        desc = m.OpposingTeam + ' on ' + str(m.MatchDate)
        match.append((m.idmatch, desc))


    # Our team - active players
    player=[]
    playernames = Player.query.filter_by(Active='Y').order_by(Player.Surname).all()
    for playername in playernames:
        player.append((playername.idplayer, playername.FirstName + ' ' + playername.Surname))


    opponent=[]
    opponent.append((0, 'New Opponent...'))

    # Racks to win - 0 thru 11 only
    i=0
    racks=[]
    while i < 12:
        racks.append((i,i))
        i = i + 1


    # Main from starts here
    matchpick = SelectField('Select Match', choices=match, coerce=int)
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
    submit = SubmitField('Create Match Result')


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


class RegistrationForm(FlaskForm):
    # TODO Implement 2FA by sending verification email
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


    def validate_username(self, username):
        user = User.query.filter_by(UserName=username.data).first()
        if user is not None:
            raise ValidationError('Username in use - Please use a different username.')


    def validate_email(self, email):
        user = User.query.filter_by(Email=email.data).first()
        if user is not None:
            raise ValidationError('Email in use - Please use a different email address.')


class BogMan(FlaskForm):
    # Create pick lists
    # Our team - active players
    player=[]
    playernames = Player.query.filter_by(Active='Y').order_by(Player.Surname).all()
    for playername in playernames:
        player.append((playername.idplayer, playername.FirstName + ' ' + playername.Surname))

    playerpick = SelectField('Select Player',
                             choices=player, coerce=int)
    bogged = RadioField('Bogged?', choices=[('Y', 'Bogged'), ('N', 'Not Bogged')], default='Y')
    bogdate = DateField('Bogged Date', validators=[DateField], default=datetime.today() , format="%Y-%m-%d")
    submit = SubmitField('Update Bog')


class UserMan(FlaskForm):
    # Create pick lists
    # Our team - active players
    player=[]
    playernames = Player.query.filter_by(Active='Y').order_by(Player.Surname).all()
    for playername in playernames:
        player.append((playername.idplayer, playername.FirstName + ' ' + playername.Surname))

    # Active Users
    user = []
    users = User.query.order_by(User.UserName).all()
    for userid in users:
        user.append((userid.id, userid.UserName + ' ' + userid.Email))

    playerpick = SelectField('Select Player', choices=player, coerce=int)
    userpick = SelectField('Select User', choices=user, coerce=int)
    submit = SubmitField('Update User')
