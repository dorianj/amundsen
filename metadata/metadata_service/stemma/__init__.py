from flask import Blueprint, Flask
from flask_restful import Api

from metadata_service.stemma.api.slack import SlackLinkAPI, SlackMessagesAPI


def init_custom_apps_and_routes(app: Flask) -> None:
    stemma_bp = Blueprint('stemma', __name__, url_prefix='/stemma')

    stemma_api = Api(stemma_bp)

    stemma_api.add_resource(SlackLinkAPI, '/slack/link')
    stemma_api.add_resource(SlackMessagesAPI, '/slack/messages')

    app.register_blueprint(stemma_bp)
