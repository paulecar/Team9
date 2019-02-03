from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, BooleanField, SubmitField, RadioField
from wtforms.widgets import FileInput
from wtforms_components import TimeField
from wtforms.validators import DataRequired, ValidationError


# Utility objects
from team9utils import hcaps, ranks, racks, roles, yn, get_est, themes
from team9.main.forms import validateScore


class AddMatch(FlaskForm):
    picks = []
    today = get_est()
    teampick = SelectField('Pick Team', choices=picks, coerce=int)
    opposingteam = StringField('Opposing Team')
    matchdate = DateField('Match Date', validators=[DateField], default=today.today(), format="%Y-%m-%d")
    starttime = TimeField('Start Time', validators=[TimeField])
    playoff = BooleanField('Playoff Match', default=False)

    submit = SubmitField('Create Match')

    def validate_opposingteam(self, opposingteam):
        # 0 means 'New team..'
        if self.teampick.data == 0:
            if len(self.opposingteam.data) == 0:
                raise ValidationError('Select Opposing Team from list or Enter a team name in the text box.')


class UpdateMatch(FlaskForm):
    picks = []
    today = get_est()
    teampick = SelectField('Pick Team', choices=picks, coerce=int)
    opposingteam = StringField('Opposing Team')
    matchdate = DateField('Match Date', validators=[DateField], default=today.today(), format="%Y-%m-%d")
    starttime = TimeField('Start Time', validators=[TimeField])
    playoff = BooleanField('Playoff Match', default=False)

    submit = SubmitField('Update Match')

    def validate_opposingteam(self, opposingteam):
        if len(self.opposingteam.data) == 0:
            raise ValidationError('Enter a team name in the text box.')


class AddSeason(FlaskForm):
    today = get_est()
    seasonname = StringField('Season Name', validators=[DataRequired()])
    startdate = DateField('Start Date', validators=[DateField], default=today.today(), format="%Y-%m-%d")
    enddate = DateField('End Date Date', validators=[DateField], default=today.today(), format="%Y-%m-%d")
    current = SelectField('Current Season Y/N', choices=yn)
    submit = SubmitField('Create Season')


class AddPlayer(FlaskForm):
    surname = StringField('Surname', validators=[DataRequired()])
    firstname = StringField('First Name', validators=[DataRequired()])
    submit = SubmitField('Create Player')


class AddMatchUp(FlaskForm):
    # Define pick lists
    player = []
    playerpick = SelectField('Select Our Player',
                             choices=player, coerce=int)
    playerrank = SelectField('Select Player Rank', choices=ranks)
    playerscore = SelectField('Our Player Scores', choices=racks, coerce=int)
    opponentname = StringField('Opponent (auto complete.... start typing)', id="tags")
    opponentrank = SelectField('Select Opponent Rank', choices=ranks)
    opponentscore = SelectField('Opponent Scores', choices=racks, coerce=int)
    mathematical_elimination = BooleanField('Mathematical elimination stops play', default=False)
    in_progress = BooleanField('Match in progress - live score', default=True)

    submit = SubmitField('Create Match Up')

    def validate_opponentname(self, opponentname):
        if len(self.opponentname.data) == 0:
            raise ValidationError("Enter Opponent's Name in the text box.")

    def validate_playerscore(self, playerscore):

        try:
            race = hcaps[self.playerrank.data][self.opponentrank.data]
        except:
            raise ValidationError('Something went wrong with race lookup (player)?')

        # Set racks on the wire automatically
        if self.playerscore.data < race[0]:
            self.playerscore.data = race[0]

        validateScore(self, race, 'player')


    def validate_opponentscore(self, opponentscore):

        try:
            race = hcaps[self.playerrank.data][self.opponentrank.data]
        except:
            raise ValidationError('Something went wrong with race lookup (player)?')

        # Set racks on the wire automatically
        if self.opponentscore.data < (race[0] * -1):
            self.opponentscore.data = race[0] * -1

        validateScore(self, race, 'opponent')


class BogMan(FlaskForm):
    today = get_est()
    bogged = SelectField('Bogged', choices=[('Y', 'Bogged'), ('N', 'Not Bogged')], default='Y')
    active = SelectField('Active Player', choices=yn, default='Y')
    bogdate = DateField('Bogged Date', validators=[DateField], default=today.today(), format="%Y-%m-%d")
    change = RadioField('Change Bog Date?', choices=[('Y', 'Change Date'), ('N', 'Ignore Date')], default='N')

    submit = SubmitField('Update Bog')


class SeasonMan(FlaskForm):
    today = get_est()
    seasonname = StringField('Update Season Name')
    startdate = DateField('Update Start Date', validators=[DateField], default=today.today(), format="%Y-%m-%d")
    enddate = DateField('Update End Date', validators=[DateField], default=today.today(), format="%Y-%m-%d")
    current = SelectField('Current Season Y/N', choices=yn, default='N')

    submit = SubmitField('Update Season')


class UploadForm(FlaskForm):
    filename = FileInput()
    submit = SubmitField('Upload')


class UserMan(FlaskForm):
    # Create pick lists
    player = []
    playerpick = SelectField('Link to Player', choices=player, coerce=int)
    userrole = SelectField('Assign / Clear User Role', choices=roles)

    submit = SubmitField('Update User')


class UserTheme(FlaskForm):
    themepick = SelectField('Select Theme', choices=themes)

    submit = SubmitField('Update Settings')
