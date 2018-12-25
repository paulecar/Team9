from team9 import db, create_app

team9 = create_app()
team9.app_context().push()

@team9.shell_context_processor
def make_shell_context():
    # Done here to support query in the /index page
    return {'db': db}

