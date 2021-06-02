import os
from typing import Dict

from amundsen_application.config import LocalConfig
from amundsen_application.stemma import init_stemma_routes
from flask import Flask


def get_access_headers(app: Flask) -> Dict:
    """
    Function to retrieve and format the Authorization Headers
    that can be passed to various microservices who are expecting that.
    :param oidc: OIDC object having authorization information
    :return: A formatted dictionary containing access token
    as Authorization header.
    """
    try:
        access_token = app.oidc.get_access_token()
        return {'Authorization': 'Bearer {}'.format(access_token)}
    except Exception:
        return {}


def get_auth_user(app: Flask) -> object:
    from flask import g

    user_info = type('UserInfo', (object,), g.oidc_id_token)
    user_info.user_id = user_info.email     # type: ignore
    return user_info


class StemmaConfig(LocalConfig):
    SLACK_CONVERSATIONS_ENABLED = os.environ.get('SLACK_CONVERSATIONS_ENABLED', False)

    INIT_CUSTOM_ROUTES = init_stemma_routes

    AUTH_USER_METHOD = get_auth_user

    REQUEST_HEADERS_METHOD = get_access_headers
