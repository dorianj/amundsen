import logging
from typing import Tuple

from flask import Flask, Response


SLACK_ENABLED_MESSAGE = "Slack Conversations are enabled for this server"
SLACK_NOT_ENABLED_MESSAGE = "Slack Conversations are disabled for this server. " \
                            "'Please enable 'SLACK_CONVERSATIONS_ENABLED' " \
                            "if you wish to use Slack Conversations'"


def init_stemma_routes(app: Flask) -> None:
    with app.app_context():
        from amundsen_application.stemma.api.slack import (
            SLACK_MESSAGES_ENDPOINT,
            SLACK_EVENTS_ENDPOINT,
            SLACK_BASE_ENDPOINT
        )

        # If Slack Conversations Enabled
        if app.config["SLACK_CONVERSATIONS_ENABLED"]:
            logging.info(SLACK_ENABLED_MESSAGE)
            # The reason to do it like this is that we are injecting slack events adapter
            # to the current app in the file
            from ..stemma.api.slack.v1 import slack_blueprint
            app.register_blueprint(slack_blueprint)
        else:
            logging.info(SLACK_NOT_ENABLED_MESSAGE)
            app.add_url_rule(SLACK_EVENTS_ENDPOINT, 'slack_events', gracefully_respond_slack, methods=["POST"])
            app.add_url_rule(SLACK_BASE_ENDPOINT + SLACK_MESSAGES_ENDPOINT, 'slack_catch_all',
                             gracefully_respond_slack, methods=["GET", "POST"])


def gracefully_respond_slack() -> Tuple[Response, int]:
    logging.info(SLACK_NOT_ENABLED_MESSAGE)
    resp = Response(SLACK_NOT_ENABLED_MESSAGE)
    # This will make sure not to retry any command in case Slack is disabled
    resp.headers['X-Slack-No-Retry'] = 1
    return resp, 405
