from team9 import team9, db
from team9.models import Player


# TODO Figure out how to use 'real' server rather than Flask test server


@team9.shell_context_processor
def make_shell_context():
    # Done here to support query in the /index page
    return {'db': db, 'Player': Player}

