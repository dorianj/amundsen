# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from databuilder.stemma.tasks.generators import get_task_generator
from databuilder.stemma.tasks.generators.relational_db import SnowflakeTaskGenerator
from databuilder.stemma.tasks.generators.search_extract import SearchIndexTaskGenerator


class TestGetGenerators(unittest.TestCase):

    def test_get_task_generator(self) -> None:
        actual_snowflake = get_task_generator('snowflake-metadata')
        self.assertEqual(actual_snowflake, SnowflakeTaskGenerator)

        actual_search_index = get_task_generator('extract-index-search')
        self.assertEqual(actual_search_index, SearchIndexTaskGenerator)
