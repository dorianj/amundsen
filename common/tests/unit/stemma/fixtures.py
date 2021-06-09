from amundsen_common.tests.fixtures import Fixtures

from amundsen_common.models.stemma.slack import SlackMessage


class StemmaFixtures(Fixtures):

    @staticmethod
    def next_slack_message() -> SlackMessage:
        key = Fixtures.next_string(length=10)
        channel = Fixtures.next_string(length=10)
        channel_id = Fixtures.next_string(length=10)
        team = Fixtures.next_string(length=10)
        text = Fixtures.next_description_source()
        thread_ts = Fixtures.next_string(length=10)
        ts = Fixtures.next_string(length=10)
        _type = Fixtures.next_string(length=10)
        author = Fixtures.next_string(length=10)

        return SlackMessage(key=key, channel=channel, channel_id=channel_id, team=team,
                            text=text, thread_ts=thread_ts, ts=ts, type=_type, author=author)


def next_slack_message() -> SlackMessage:
    return StemmaFixtures.next_slack_message()
