# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from amundsen_application.stemma.api.slack import custom_replies


class SlackResponsesTest(unittest.TestCase):

    def test_not_in_thread(self) -> None:
        """
        :return:
        """
        img_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ4JpT6dM9YyqlvR681I_wALow-EExEcqYCmg&usqp=CAU"
        expected = {
            'meaning of life': [
                {
                    "type": "image",
                    "title": {
                        "type": "plain_text",
                        "text": "You wanted to know the meaning of life, right?"
                    },
                    "block_id": "meaning_of_life",
                    "image_url": img_url,
                    "alt_text": "Meaning of Life"
                }
            ],
            'hello': [
                {
                    "type": "image",
                    "title": {
                        "type": "plain_text",
                        "text": "helloooo!"
                    },
                    "block_id": "hello",
                    "image_url": "https://media.tenor.com/images/4627bbfa1353325d94fd226b160afd7d/tenor.gif",
                    "alt_text": "Hello"
                }
            ]
        }

        actual = custom_replies.CUSTOM_REPLIES
        self.assertEqual(expected, actual)
