import unittest

from .fixtures import next_slack_message


class TestStemmaFixtures(unittest.TestCase):
    def test_0001_next_slack_message(self) -> None:
        slack = next_slack_message()
        self.assertEqual('zabcdefghi001361', slack.key)
        self.assertEqual('klmnopqrst001372', slack.channel)
        self.assertEqual('vwxyzabcde001383', slack.channel_id)
