import os
from abc import abstractmethod

from databuilder.extractor.snowflake_metadata_extractor import SnowflakeMetadataExtractor
from databuilder.extractor.sql_alchemy_extractor import SQLAlchemyExtractor
from databuilder.stemma.tasks.generators.base_task_generator import TaskGenerator


class RelationalDbTaskGenerator(TaskGenerator):
    """
    All relational DB configs should use the following keys, where applicable. If a given
    value does not exist for the database it does not need to be provided:
    {
        "USERNAME": 'un',
        "PASSWORD": 'adad',
        "HOST": 'asdad',
        "PORT": 123
    }
    If a specific database requrires more inputs they may be added as well but we should
    keep track of the inputs in order to standardize them across use-cases.
    """
    def __init__(self) -> None:
        self.database = os.environ['RDB_DATABASE_NAME']
        super().__init__()

    def add_instance_confs(self) -> None:
        conn_str_key = f'{self.extractor_instance.get_scope()}.extractor.sqlalchemy.{SQLAlchemyExtractor.CONN_STRING}'
        self.conf_dict[conn_str_key] = self.get_conn_string()

    @abstractmethod
    def get_conn_string(self) -> str:
        pass

    @abstractmethod
    def _set_extractor_class(self) -> None:
        pass


class SnowflakeTaskGenerator(RelationalDbTaskGenerator):
    EXTRACTOR_CLASS = SnowflakeMetadataExtractor  # type: ignore
    REQUIRED_SECRETS = [
        'USERNAME',
        'PASSWORD',
        'ACCOUNT',
        'WAREHOUSE'
    ]
    # Optional secrets:
    #   - ROLE

    def add_instance_confs(self) -> None:
        super().add_instance_confs()

        # Add Ignored Columns
        ignored_schemas = ['\'INFORMATION_SCHEMA\'']
        where_clause = f"WHERE c.TABLE_SCHEMA not in ({','.join(ignored_schemas)})"
        where_conf_key = f'{self.extractor_instance.get_scope()}.{self.extractor_instance.WHERE_CLAUSE_SUFFIX_KEY}'
        self.conf_dict[where_conf_key] = where_clause

        # Add database name
        db_conf_key = f'{self.extractor_instance.get_scope()}.{self.extractor_instance.SNOWFLAKE_DATABASE_KEY}'
        self.conf_dict[db_conf_key] = f'"{self.database}"'  # Always quote snowflake databases

    def get_conn_string(self) -> str:
        conn_str = 'snowflake://{USERNAME}:{PASSWORD}@{ACCOUNT}/?warehouse={WAREHOUSE}'
        conn_fmt = conn_str.format(**self.conn_secrets)
        role = self.conn_secrets.get('ROLE')
        if role:
            conn_fmt += f'&role={role}'
        return conn_fmt
