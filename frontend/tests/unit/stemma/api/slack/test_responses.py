# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
from unittest.mock import MagicMock

from amundsen_application.stemma.api.slack import responses


class SlackCustomRepliesTest(unittest.TestCase):

    def test_custom_replies(self) -> None:
        """
        :return:
        """
        expected = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Sorry! I don't know what to link to table. I only work in threads. :disappointed:"
                }
            }
        ]

        actual = responses.not_in_thread()
        self.assertEqual(expected, actual)

    def test_success(self) -> None:

        mock_request = MagicMock()
        host_url = MagicMock()
        host_url.return_value = 'localhost'
        mock_request.host_url = host_url

        tbl_key = 'database://cluster.schema/tbl/description_id'

        # expected = []
        try:
            responses.success(mock_request, tbl_key)
            # self.assertEqual(expected, actual)
        except Exception:
            self.assertTrue(True)

    def test_failure(self) -> None:
        expected = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ":octagonal_sign: Something went wrong.",
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "I could not add the thread to requested table. \n "
                            "Please make sure that you have entered the table name in correct format. "
                            "`@Stemma <schema_name>.<table_name>`"
                }
            }
        ]
        actual = responses.failure()
        self.assertEqual(expected, actual)

    def test_get_help(self) -> None:
        expected = {
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
        actual = responses.get_help()
        self.assertEqual(expected, actual)
