import json
from http import HTTPStatus
from typing import Iterable, Mapping, Union

from amundsen_common.models.stemma.slack import SlackMessageSchema
from flask import request
from flask_restful import Resource

from metadata_service.exception import NotFoundException
from metadata_service.proxy import get_proxy_client


class SlackLinkAPI(Resource):
    def __init__(self) -> None:
        self.client = get_proxy_client()
        super(SlackLinkAPI, self).__init__()

    def put(self) -> Iterable[Union[Mapping, int, None]]:
        """
        API to add a slack thread to a table
        """

        try:
            data = json.loads(request.data)
            # noinspection PyUnresolvedReferences
            resource_key = self.client.add_slack_thread(message_data=data)      # type: ignore
            return {'message': f'SUCCESS', 'resource_key': resource_key}, HTTPStatus.OK
        except NotFoundException:
            return {'message': f'KEY NOT FOUND'}, HTTPStatus.BAD_REQUEST
        except Exception as e:
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
        try:
            data = json.loads(request.data)
            # noinspection PyUnresolvedReferences
            slack_messages = self.client.get_slack_messages(resource_key=data['resource_key'])      # type: ignore
            return SlackMessageSchema().dump(slack_messages, many=True), HTTPStatus.OK
        except NotFoundException:
            return {'message': f'Resource key not found'}, HTTPStatus.BAD_REQUEST
        except Exception as e:
            return {'message': f'Internal Server Error Occurred'}, HTTPStatus.INTERNAL_SERVER_ERROR
