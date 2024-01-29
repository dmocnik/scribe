from flask import Blueprint
from flask_swagger_ui import get_swaggerui_blueprint
from .swagger_config import swagger_config

def setup_swagger(app, config):

    # Get swagger blueprint
    swaggerui_blueprint = get_swaggerui_blueprint(
        config.SWAGGER_URL,
        config.API_URL,
        config=swagger_config
    )

    # Register the blueprint with the app
    app.register_blueprint(swaggerui_blueprint)