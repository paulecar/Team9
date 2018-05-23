from team9 import team9, db
from team9.models import Player

@team9.shell_context_processor
def make_shell_context():
    return {'db': db, 'Player': Player}

