import os
from typing import Dict

from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
from slack_sdk import WebClient

slack_client = WebClient(token=os.environ.get('SLACK_BOT_TOKEN'))
_CACHE = CacheManager(**parse_cache_config_options({'cache.regions': 'stemma_slack_client',
                                                    'cache.atlas_proxy.type': 'memory'}))


@_CACHE.cache("_get_permalink")
def _get_slack_permalink(channel_id: str, thread_ts: str) -> str:
    """
    """
    permalink_response = slack_client.chat_getPermalink(
        channel=channel_id, message_ts=thread_ts
    )
    return permalink_response.get("permalink")


@_CACHE.cache("_get_slack_user_info")
def _get_slack_user_info(slack_user_id: str) -> dict:
    """
    """
    user_response = slack_client.users_info(user=slack_user_id)
    user = user_response.get("user", {})
    profile = user.get("profile", {})
    return {
        "id": user.get("id"),
        "display_name": profile.get("display_name"),
        "real_name": profile.get("real_name"),
        "first_name": profile.get("first_name"),
        "last_name": profile.get("last_name"),
        "image_original": profile.get("image_original"),
        "image_72": profile.get("image_72"),
    }


@_CACHE.cache("_get_channel_info")
def _get_channel_info(channel_id: str) -> dict:
    channel_response = slack_client.conversations_info(channel=channel_id)
    channel = channel_response.get("channel", {})
    return channel.get("name")


def post_message_to_slack(channel: str, response: list, text: str, ts: str) -> None:
    """
    Posts a message in a slack thread
    """
    slack_client.chat_postMessage(channel=channel,
                                  blocks=response,
                                  text=text,
                                  thread_ts=ts)


def retrieve_message_details(thread_ts: str, channel: str) -> Dict:
    """
    """
    message_response = slack_client.conversations_history(
        channel=channel,
        inclusive=True,
        oldest=thread_ts,
        limit=1
    )
    message_data = message_response.get("messages", [])[0]
    channel_name = _get_channel_info(channel)

    return {
        "channel": channel_name,
        "channel_id": channel,
        "key": f'{channel}/{message_data["thread_ts"]}',
        "team": message_data["team"],
        "text": message_data["text"],
        "thread_ts": message_data["thread_ts"],
        "ts": message_data["ts"],
        "type": message_data["type"],
        "author": message_data["user"],
    }


def _retrieve_message_replies(thread_ts: str, channel: str) -> int:
    """
    FixMe: Taking too long for each message. think of cache this response
    """
    replies_response = slack_client.conversations_replies(
        channel=channel,
        ts=thread_ts,
        limit=100
    )

    return len(replies_response["messages"])


def retrieve_message_components(message: dict) -> Dict:
    """
    Retrieves the message details, its permalink and the user
    information of the sender. This uses the cached response for user info and the
    message permalink, but always fetches the latest information of a message, to get
    the correct number of replies and edits made.
    """
    _channel_id = message["channel_id"]
    _ts = message["thread_ts"]

    return {
        "message": message,
        "replies": _retrieve_message_replies(_ts, _channel_id),
        "author": _get_slack_user_info(message["author"]),
        "permalink": _get_slack_permalink(_channel_id, _ts)
    }
