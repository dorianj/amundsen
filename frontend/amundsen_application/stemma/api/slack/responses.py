from typing import Dict, List
from urllib.parse import urljoin

from flask import Request

from amundsen_application.api.utils.metadata_utils import TableUri


def not_in_thread() -> List:
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Sorry! I don't know what to link to table. I only work in threads. :disappointed:"
            }
        }
    ]


def success(request: Request, key: str) -> List:
    table_uri = TableUri.from_uri(key)
    stemma_url = urljoin(request.host_url,
                         f'table_detail/{table_uri.cluster}/{table_uri.database}/'
                         f'{table_uri.schema}/{table_uri.table}')
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f':tada: I have linked this thread to this table: `{key}`',
            }
        },
        {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": "View this thread in Stemma Application: "
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Table Detail",
                },
                "value": "table_detail",
                "url": stemma_url,
                "action_id": "button-action"
            }
        }
    ]


def failure(user_input: str, text: str) -> List:
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": ":octagonal_sign: Something went wrong.",
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f'This is what you sent: `{user_input}`'
                },
                {
                    "type": "mrkdwn",
                    "text": f'This is what we processed: `{text}`',
                }
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "'I could not add the thread to requested table. \n "
                        "Please make sure that you have entered the table name in correct format. "
                        "`@Stemma <schema_name>.<table_name>`"
            }
        }
    ]


def get_help() -> Dict:
    return {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "I only work in Slack Threads. Every time you tag me in a slack thread,"
                            "I will link that thread to your table in Stemma."
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Please make sure that you have entered the table name in correct format. "
                            "`@Stemma <schema_name>.<table_name>`"
                }
            }
        ]
    }
