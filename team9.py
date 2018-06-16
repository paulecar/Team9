from team9 import team9, db

@team9.shell_context_processor
def make_shell_context():
    # Done here to support query in the /index page
    return {'db': db}

