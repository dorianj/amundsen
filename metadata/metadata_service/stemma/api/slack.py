import json
import logging
import os
from http import HTTPStatus
from typing import Iterable, Mapping, Union

from amundsen_common.models.stemma.slack import SlackMessageSchema
from amundsen_common.utils.hmac_utils import verify_token
from flask import request
from flask_restful import Resource

from metadata_service.exception import NotFoundException
from metadata_service.proxy import get_proxy_client

LOGGER = logging.getLogger(__name__)


class SlackLinkAPI(Resource):
    def __init__(self) -> None:
        self.client = get_proxy_client()
        super(SlackLinkAPI, self).__init__()

    def put(self) -> Iterable[Union[Mapping, int, None]]:
        """
        API to add a slack thread to a table
        """
        data = {}
        try:
            request_token = request.args.get('token')
            if not request_token:
                LOGGER.error('Request token not found')
                return {'message': 'Request token not found'}, HTTPStatus.BAD_REQUEST

            if not verify_token(request_token, os.environ.get('SLACK_SIGNING_SECRET'), request.data):
                LOGGER.error("Slack Signing Secrets do not match.")
                return {'message': 'Slack Signing Secrets do not match'}, HTTPStatus.BAD_REQUEST

            data = json.loads(request.data)
            # noinspection PyUnresolvedReferences
            resource_key = self.client.add_slack_thread(message_data=data)      # type: ignore
            return {'message': f'SUCCESS', 'resource_key': resource_key}, HTTPStatus.OK
        except NotFoundException:
            LOGGER.error(f'NotFoundException: Resource Key not found: {data.get("table_name")}')
            return {'message': f'Key not found'}, HTTPStatus.BAD_REQUEST
        except Exception as e:
            LOGGER.error(f'Internal server error occurred when linking the table to slack thread: {e}')
            return {'message': f'FAILURE'}, HTTPStatus.INTERNAL_SERVER_ERROR


class SlackMessagesAPI(Resource):
    """
    SlackMessagesAPI
    """
    def __init__(self) -> None:
        self.client = get_proxy_client()
        super(SlackMessagesAPI, self).__init__()

    def post(self) -> Iterable[Union[Mapping, int, None]]:
        """
        API to retrieve slack threads linked to a Resource
        """
        data = {}
        try:
            data = json.loads(request.data)
            # noinspection PyUnresolvedReferences
            slack_messages = self.client.get_slack_messages(resource_key=data['resource_key'])      # type: ignore
            return SlackMessageSchema().dump(slack_messages, many=True), HTTPStatus.OK
        except NotFoundException:
            LOGGER.error(f'NotFoundException: Resource Key not found: {data.get("resource_key")}')
            return {'message': f'Resource key not found'}, HTTPStatus.BAD_REQUEST
        except Exception as e:
            LOGGER.error(f'Internal server error occurred when getting the slack threads: {e}')
            return {'message': f'Internal Server Error Occurred'}, HTTPStatus.INTERNAL_SERVER_ERROR
