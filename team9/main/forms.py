from flask_wtf import FlaskForm
from wtforms import SelectField, BooleanField, SubmitField, HiddenField
from wtforms.validators import ValidationError


# Helpers
from team9utils import hcaps, racks


# Common validation logic for MatchUp scores
def validateScore(form, race, field):
    if field == 'player':
        if form.playerscore.data > race[1]:
            raise ValidationError('Score appears to be more than required number of racks')
        if form.playerscore.data < race[0]:
            raise ValidationError('Score appears to be less than racks given on the wire?')
    else:
        if form.opponentscore.data > race[1]:
            raise ValidationError('Score appears to be more than required number of racks')
        if form.opponentscore.data < (race[0] * -1):
            raise ValidationError('Player score appears to be less than racks given on the wire?')

    if form.opponentscore.data < race[1] \
            and form.playerscore.data < race[1] \
            and not (form.mathematical_elimination.data or form.in_progress.data):
        raise ValidationError('One of the players must reach the target number of racks : ' + race[1].__str__())

    return


class LiveScore(FlaskForm):
    playerscore = SelectField('Our Player Scores', choices=racks, coerce=int)
    opponentscore = SelectField('Opponent Scores', choices=racks, coerce=int)
    mathematical_elimination = BooleanField('Mathematical elimination stops play', default=False)
    in_progress = BooleanField('Match in progress - live score', default=False)
    playerrank = HiddenField('Player Rank')
    opponentrank = HiddenField('Opp Rank')

    submit = SubmitField('Update Score')

    def validate_playerscore(self, playerscore):
        try:
            race = hcaps[self.playerrank.data][self.opponentrank.data]
        except:
            raise ValidationError('Something went wrong with race lookup (player)?')

        validateScore(self, race, 'player')

    def validate_opponentscore(self, opponentscore):
        try:
            race = hcaps[self.playerrank.data][self.opponentrank.data]
        except:
            raise ValidationError('Something went wrong with race lookup (opponent)?')

        validateScore(self, race, 'opponent')
