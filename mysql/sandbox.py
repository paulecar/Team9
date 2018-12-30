from team9 import create_app
team9 = create_app()
team9.app_context().push()
from flask_bootstrap import Bootstrap, bootstrap_find_resource

bootstrap = Bootstrap()

print(bootstrap_find_resource('css/bootstrap.css', cdn='bootstrap', use_minified=True))

print(team9.extensions['bootstrap'], type(team9.extensions['bootstrap']))

for k, v in team9.extensions['bootstrap']['cdns'].items():
    print("Item:", k, v)

team9.extensions['bootstrap']['cdns']['bootstrap'] = "//stackpath.bootstrapcdn.com/bootswatch/3.3.7/yeti/"

cdns = team9.extensions['bootstrap']['cdns']
resource_url = cdns['bootstrap'].get_resource_url('foo')
print(resource_url)

