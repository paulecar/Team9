from datetime import datetime
from dateutil import tz
from flask import current_app
from team9 import db
from team9.models import KeyValueMap

# Amsterdam team 9 handicap races table
hcaps={}

hcaps.update({'P' : {'P' : [0, 9], 'O+' : [-2, 10],  'O' : [-3, 10], 'A+' : [-3, 9],
                     'A' : [-4, 10], 'B+' : [-5, 10],  'B' : [-6, 11],  'C+' : [-6, 10],
                     'C' : [-8, 11], 'D+' : [-8, 10], 'D' : [-9, 11]}})

hcaps.update({'O+' : {'P' : [2, 10], 'O+' : [0, 9],  'O' : [-1, 9], 'A+' : [-2, 9],
                      'A' : [-3, 10], 'B+' : [-4, 9],  'B' : [-5, 10],  'C+' : [-6, 11],
                      'C' : [-7, 11], 'D+' : [-7, 10], 'D' : [-8, 10]}})

hcaps.update({'O' : {'P' : [3, 10], 'O+' : [1, 9],  'O' : [0, 9], 'A+' : [-1, 9],
                     'A' : [-2, 8], 'B+' : [-3, 8],  'B' : [-4, 9],  'C+' : [-5, 10],
                     'C' : [-6, 11], 'D+' : [-7, 11], 'D' : [-7, 10]}})

hcaps.update({'A+' : {'P' : [3, 9], 'O+' : [2, 9],  'O' : [1, 9], 'A+' : [0, 8],
                      'A' : [-1, 8], 'B+' : [-2, 8],  'B' : [-3, 8],  'C+' : [-4, 9],
                      'C' : [-5, 10], 'D+' : [-6, 11], 'D' : [-7, 11]}})

hcaps.update({'A' : {'P' : [4, 10], 'O+' : [3, 10],  'O' : [2, 8], 'A+' : [1, 8],
                     'A' : [0, 8], 'B+' : [-1, 8],  'B' : [-2, 8],  'C+' : [-3, 8],
                     'C' : [-4, 9], 'D+' : [-5, 10], 'D' : [-6, 11]}})

hcaps.update({'B+' : {'P' : [5, 10], 'O+' : [4, 9],  'O' : [3, 8], 'A+' : [2, 8],
                      'A' : [1, 8], 'B+' : [0, 7],  'B' : [-1, 7],  'C+' : [-2, 7],
                      'C' : [-3, 8], 'D+' : [-4, 9], 'D' : [-5, 10]}})

hcaps.update({'B' : {'P' : [6, 11], 'O+' : [5, 10],  'O' : [4, 9], 'A+' : [3, 8],
                     'A' : [2, 8], 'B+' : [1, 7],  'B' : [0, 7],  'C+' : [-1, 7],
                     'C' : [-2, 7], 'D+' : [-3, 8], 'D' : [-4, 9]}})

hcaps.update({'C+' : {'P' : [6, 10], 'O+' : [6, 11],  'O' : [5, 10], 'A+' : [4, 9],
                      'A' : [3, 8], 'B+' : [2, 7],  'B' : [1, 7],  'C+' : [0, 7],
                      'C' : [-1, 7], 'D+' : [-2, 7], 'D' : [-3, 8]}})

hcaps.update({'C' : {'P' : [8, 11], 'O+' : [7, 11],  'O' : [6, 11], 'A+' : [5, 10],
                     'A' : [4, 9], 'B+' : [3, 8],  'B' : [2, 7],  'C+' : [1, 7],
                     'C' : [0, 7], 'D+' : [-1, 7], 'D' : [-2, 7]}})

hcaps.update({'D+' : {'P' : [8, 10], 'O+' : [7, 10],  'O' : [7, 11], 'A+' : [6, 11],
                      'A' : [5, 10], 'B+' : [4, 9],  'B' : [3, 8],  'C+' : [2, 7],
                      'C' : [1, 7], 'D+' : [0, 7], 'D' : [-1, 7]}})

hcaps.update({'D' : {'P' : [9, 11], 'O+' : [8, 10],  'O' : [7, 10], 'A+' : [7, 11],
                     'A' : [6, 11], 'B+' : [5, 10],  'B' : [4, 9],  'C+' : [3, 8],
                     'C' : [2, 7], 'D+' : [1, 7], 'D' : [0, 7]}})


# BCA player skill levels
ranks=[('P',  'Pro'),
       ('O+', 'Open +'),
       ('O',  'Open'),
       ('A+', 'A+'),
       ('A',  'A'),
       ('B+', 'B+'),
       ('B',  'B'),
       ('C+', 'C+'),
       ('C',  'C'),
       ('D+', 'D+'),
       ('D',  'D')]


# Racks to win - 0 thru 11 only
i = 0
racks=[]
while i < 12:
    racks.append((i, i))
    i = i + 1


# User roles
roles = [('None', 'None'),
         ('Admin', 'Administrator'),
         ('Helper', 'Helper')]


# Bootstrap themes
themes = [('default', 'Default'),
          ('cerulean', 'Cerulean'),
          ('cosmo', 'Cosmo'),
          ('cyborg', 'Cyborg'),
          ('darkly', 'Darkly'),
          ('flatly', 'Flatly'),
          ('journal', 'Journal'),
          ('lumen', 'Lumen'),
          ('paper', 'Paper'),
          ('readable', 'Readable'),
          ('sandstone', 'Sandstone'),
          ('simplex', 'Simplex'),
          ('slate', 'Slate'),
          ('spacelab', 'Spacelab'),
          ('superhero', 'Superhero'),
          ('united', 'United'),
          ('yeti', 'Yeti')]

# Yes/No selection
yn = [('Y', 'Yes'),
      ('N', 'No')]

# Timezones for conversion
from_zone = tz.gettz('UTC')
to_zone = tz.gettz('America/New_York')

# AWS host is running in UTC, but this will force conversion to EST
def get_est():
    utc = datetime.utcnow().replace(tzinfo=from_zone)
    est = est = utc.astimezone(to_zone)
    return est


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def getRace(playerrank, opponentrank):
    race = hcaps[playerrank][opponentrank]
    if race[0] < 0:
        wire = 0
        oppwire = race[0] * -1
    else:
        wire = race[0]
        oppwire = 0

    return wire, oppwire, race


def setWinner(race, playerscore, opponentscore, math_elim):
    if playerscore < race[1] and opponentscore < race[1] and not math_elim:
        result = 'I'
    elif playerscore > opponentscore:
        result = 'W'
    else:
        result = 'L'

    return result


def kvmSet(_key, _value):
    KeyValueMap.query.filter_by(key=_key).delete()
    kvm = KeyValueMap(key=_key, value=_value)
    db.session.add(kvm)
    db.session.commit()


def kvmGet(_key):
    kvm = KeyValueMap.query.filter_by(key=_key).first()
    return kvm.value


