from typing import Any

from .relational_db import SnowflakeTaskGenerator
from .search_extract import SearchIndexTaskGenerator

TASK_MAP = {
    # Extract databases
    'snowflake-metadata': SnowflakeTaskGenerator,

    # Index in Search
    'extract-index-search': SearchIndexTaskGenerator

}


def get_task_generator(task_type: str) -> Any:
    return TASK_MAP[task_type]
