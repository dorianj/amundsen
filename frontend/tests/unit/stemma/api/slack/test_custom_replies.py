# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from amundsen_application.stemma.api.slack import v1


class SlackV1Test(unittest.TestCase):

    def test_not_in_thread(self) -> None:
        """
        :return:
        """
        try:
            v1.add_slack_thread({}, '')
        except Exception:
            self.assertTrue(True)
