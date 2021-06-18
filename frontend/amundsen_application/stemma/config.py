import os
import json

from typing import Dict
from flask import Flask, session

from amundsen_application.config import LocalConfig
from amundsen_application.stemma import init_stemma_routes
from amundsen_application.models.user import load_user, User


def get_access_headers(app: Flask) -> Dict:
    """
    Function to retrieve and format the Authorization Headers
    that can be passed to various microservices who are expecting that.
    :param oidc: OIDC object having authorization information
    :return: A formatted dictionary containing access token
    as Authorization header.
    """
    try:
        # noinspection PyUnresolvedReferences
        access_token = json.dumps(app.auth_client.token)
        return {'Authorization': 'Bearer {}'.format(access_token)}
    except Exception:
        return {}


def get_auth_user(app: Flask) -> User:
    user_info = load_user(session.get("user"))
    return user_info


class StemmaConfig(LocalConfig):
    SLACK_CONVERSATIONS_ENABLED = os.environ.get('SLACK_CONVERSATIONS_ENABLED', False)

    INIT_CUSTOM_ROUTES = init_stemma_routes

    AUTH_USER_METHOD = get_auth_user

    REQUEST_HEADERS_METHOD = get_access_headers
