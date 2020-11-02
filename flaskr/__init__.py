import os

from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY=False,
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
    )

    if test_config is None:
        app.config.from_object('config.Config')
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    print()

    from . import db, index, groups, player, riot, teams
    db.init_app(app)

    app.register_blueprint(index.bp)
    app.register_blueprint(groups.bp)
    app.register_blueprint(player.bp)
    app.register_blueprint(riot.bp)
    app.register_blueprint(teams.bp)

    return app