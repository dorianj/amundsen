import logging
import textwrap
from typing import List

from amundsen_common.models.stemma.slack import SlackMessage

from metadata_service.entity.resource_type import ResourceType
from metadata_service.exception import NotFoundException
from metadata_service.proxy.neo4j_proxy import Neo4jProxy
from metadata_service.proxy.statsd_utilities import timer_with_counter

LOGGER = logging.getLogger(__name__)


class StemmaProxy(Neo4jProxy):

    @timer_with_counter
    def add_slack_thread(self, *, message_data: dict, resource_type: ResourceType = ResourceType.Table) -> None:
        """
        Please note that key of SlackMessage is "<channel_id>/<thread_ts>"
        """
        resource_name = message_data.pop("table_name")
        LOGGER.info("trying to add a new thread")
        validation_query = \
            'MATCH (n:{resource_type}) WHERE n.key ENDS WITH $resource_name return n'.format(
                resource_type=resource_type.name
            )

        upsert_slack_thread_query = textwrap.dedent("""
        MERGE (u:SlackThread {key: $key})
        on CREATE SET u={key: $key, channel: $channel, author: $author, channel_id: $channel_id,
        team: $team, text: $text, thread_ts: $thread_ts, ts: $ts, type: $type}
        on MATCH SET u={key: $message_key, channel: $channel, author: $author, channel_id: $channel_id,
        team: $team, text: $text, thread_ts: $thread_ts, ts: $ts, type: $type}
        """)

        upsert_slack_thread_relation_query = textwrap.dedent("""
        MATCH (n1:SlackThread {{key: $key}}), (n2:{resource_type}) WHERE n2.key ENDS WITH $resource_name
        MERGE (n1)-[r1:THREAD_OF]->(n2)
        RETURN n1.key, n2.key
        """.format(resource_type=resource_type.name))

        try:
            tx = self._driver.session().begin_transaction()
            tbl_result = tx.run(validation_query, {'resource_name': resource_name}).single()
            if not tbl_result:
                raise NotFoundException('Key {} does not exist'.format(resource_name))

            # upsert the node
            tx.run(upsert_slack_thread_query, **message_data)
            result = tx.run(upsert_slack_thread_relation_query,
                            {'key': message_data.get("key"), 'resource_name': resource_name}).single()
            if not result:
                raise RuntimeError('Failed to create relation between '
                                   'slack thread and resource {resource} of resource type: {resource_type}')
            tx.commit()
            return result[1]
        except Exception as e:
            if not tx.closed():
                tx.rollback()
            # propagate the exception back to api
            raise e

    @timer_with_counter
    def get_slack_messages(self, *, resource_key: str) -> List:
        """
        """
        slack_threads_query = textwrap.dedent("""
        Match(n:SlackThread)-[THREAD_OF]->({key: $key})
        RETURN n as message
        ORDER BY n.thread_ts DESC
        """)

        records = self._execute_cypher_query(statement=slack_threads_query,
                                             param_dict={'key': resource_key})

        results = []
        for record in records:
            results.append(SlackMessage(**record['message']))

        return results
