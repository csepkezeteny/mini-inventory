from pathlib import Path
from flask import Flask

from .database import init_app as init_database


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev-only-change-before-deployment",
        DATABASE=str(Path(app.instance_path) / "inventory.sqlite"),
    )

    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    init_database(app)

    from .routes import bp
    app.register_blueprint(bp)

    return app
