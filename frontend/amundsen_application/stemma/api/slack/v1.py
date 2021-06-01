import json
import logging
import os
import re
from http import HTTPStatus
from typing import Tuple, Dict

from amundsen_application.stemma.api.slack import (
    responses,
    client,
    SLACK_BASE_ENDPOINT,
    SLACK_EVENTS_ENDPOINT,
    SLACK_MESSAGES_ENDPOINT)
from amundsen_application.stemma.api.slack.custom_replies import CUSTOM_REPLIES
from flask import Blueprint, Response, jsonify, make_response, request, current_app as app
from slackeventsapi import SlackEventAdapter

from amundsen_application.api.utils.request_utils import request_metadata, get_query_param

slack_blueprint = Blueprint('slack', __name__, url_prefix=SLACK_BASE_ENDPOINT)
slack_events_adapter = SlackEventAdapter(os.environ.get('SLACK_SIGNING_SECRET'),
                                         SLACK_EVENTS_ENDPOINT, app)
LOGGER = logging.getLogger(__name__)


@slack_events_adapter.on("url_verification")
def url_verification(data: dict) -> Dict:
    LOGGER.info("Slack Event Triggered: 'url_verification'")
    return data


@slack_events_adapter.on("app_mention")
def app_mention_event(data: dict) -> None:
    LOGGER.info("Slack Event Triggered: 'app_mention'")
    message = data["event"]
    channel = message["channel"]
    initial_text = ''
    text = ''
    thread = message.get('thread_ts')

    try:
        initial_text = message['text'].split(' ', 1)[1].strip()
        text = initial_text.replace('.', '/').replace(' ', '/')
        text = re.sub("[^A-Za-z0-9/\-_]", "", text)  # noqa: W605
    except Exception as ex:
        LOGGER.exception(ex)
        LOGGER.error("Failed to parse the user input to link Slack Thread")
        LOGGER.error(f'Following is the event data: {data}')

    # This is to make interactive
    custom_reply_key = get_custom_reply_key(text)

    if custom_reply_key:
        response = CUSTOM_REPLIES[custom_reply_key]
    elif not thread:
        response = responses.not_in_thread()
    else:
        response_data, status = add_slack_thread(message, text)
        if status == HTTPStatus.OK:
            key = response_data["resource_key"]
            response = responses.success(request, key)

        else:
            response = responses.failure(initial_text, text)
    _response_text = f'This is what you sent: `{initial_text}`'
    return client.post_message_to_slack(channel, response, _response_text, thread)


def get_custom_reply_key(message: str) -> str:
    _text = ''
    for text, response in CUSTOM_REPLIES.items():
        if text in message.lower():
            _text = text
            break
    return _text


def add_slack_thread(message: dict, table_name: str) -> Tuple:
    try:
        url = f'{app.config["METADATASERVICE_BASE"]}/stemma/slack/link'
        data = client.retrieve_message_details(
            message['thread_ts'],
            message["channel"]
        )
        data.update({'table_name': table_name})
        response = request_metadata(url=url, method='PUT', data=json.dumps(data))
        status_code = response.status_code
        response_data = response.json()
        return response_data, status_code
    except Exception as e:
        LOGGER.exception(f'Failed to link slack thread to resource: {e}')
        return e, HTTPStatus.INTERNAL_SERVER_ERROR


@slack_blueprint.route('/slash/help', methods=['GET', 'POST'])
def slack_slash_help() -> Response:
    """
    Placeholder for the Slack Help Command
    """
    LOGGER.info("Slack Help Command Triggered")
    response = responses.get_help()

    return make_response(jsonify(response), 200)


@slack_blueprint.route(SLACK_MESSAGES_ENDPOINT, methods=['GET', 'POST'])
def get_slack_messages() -> Response:
    """
    Placeholder for the Slack Help Command
    """
    LOGGER.info("Get Slack Threads")

    if request.method == 'POST':
        args = request.get_json()
        resource_key = get_query_param(args, 'key')
    else:
        resource_key = get_query_param(request.args, 'key', 'Endpoint takes a "key" parameter')

    try:
        url = f'{app.config["METADATASERVICE_BASE"]}/stemma/slack/messages'
        data = {'resource_key': resource_key}
        response = request_metadata(url=url, method='POST', data=json.dumps(data))
        status_code = response.status_code
        conversations = []
        if status_code == HTTPStatus.OK:
            response_message = "Success"
            messages = response.json()
            for message in messages:
                conversations.append(client.retrieve_message_components(message))
        else:
            response_message = "An error occurred"

        payload = {
            'message': response_message,
            'conversations': conversations,
        }
        return make_response(jsonify(payload), status_code)
    except Exception as e:
        message = 'Encountered exception: ' + str(e)
        logging.exception(message)
        payload = jsonify({'msg': message})
        return make_response(payload, HTTPStatus.INTERNAL_SERVER_ERROR)
