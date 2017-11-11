import os
from flask.ext.script import Manager  #version may differ from that of ClaimsAIR
from flask.ext.migrate import Migrate, MigrateCommand

from app import app, db #from the app file import the app and db objects

app.config.from_object(os.environ['APP_SETTINGS'])

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand) #allows us to run migrations from the command line

if __name__ == '__main__':
    manager.run()