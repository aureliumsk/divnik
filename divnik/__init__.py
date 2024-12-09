from flask import Flask
from werkzeug.exceptions import HTTPException
import os
import tomllib
import logging


logger = logging.getLogger(f"{__package__}.init")


def create_app():
    app = Flask(__package__, instance_relative_config=True)

    os.makedirs(app.instance_path, exist_ok=True)

    from .log import configure_logging

    configure_logging()

    try:
        app.config.from_file(filename="config.toml", load=tomllib.load, text=False)
    except FileNotFoundError:
        logger.critical("Configuration file doesn't exists!")
        exit(3)

    from . import db

    with app.app_context():
        db.init_db()
        with app.open_resource("schema.sql", "r") as f:
            sc = f.read()
        con = db.get_db()
        cur = con.cursor()
        cur.executescript(sc)
        cur.close()
        con.commit()

    from . import pages, auth

    app.register_blueprint(pages.blueprint)
    app.register_blueprint(auth.blueprint)

    auth.register_functions(app)

    from .handlers import register_handlers
    
    register_handlers(app)

    return app