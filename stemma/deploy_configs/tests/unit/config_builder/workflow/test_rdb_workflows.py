import unittest
from test.support import EnvironmentVarGuard  # type: ignore

from amundsen_common.stemma.secrets.manager.environ import EnvironSecretManager

from config_builder.workflow.rdb import RdbTasks, RdbWorkflowItem, RdbWorkflows


class TestBaseWorkflowConf(unittest.TestCase):

    def setUp(self) -> None:
        self.env = EnvironmentVarGuard()
        self.env.set('SECRET_MANAGER_CLASS', 'amundsen_common.stemma.secrets.manager.environ.EnvironSecretManager')
        self.sm = EnvironSecretManager(None, {
            'secrets': {
                'TYPE': 'snowflake',
                'DATABASES': [
                    {
                        'NAME': 'db1',
                        'METADATA': False,
                        'STATS': True
                    },
                    {
                        'NAME': 'db2',
                        'METADATA': True,
                        'STATS': False
                    }
                ]
            }
        })

    def test_rdb_tasks(self) -> None:
        task = RdbTasks()
        self.assertFalse(task.metadata)
        self.assertFalse(task.stats)

    def test_rdb_workflow(self) -> None:
        self.exampleWf = RdbWorkflows(
            RdbWorkflowItem(
                self.sm,
                schedule='*/1 * * * *',
                tasks=RdbTasks(stats=True)
            ),
            RdbWorkflowItem(
                self.sm,
                schedule='59 23 1,7,14,21 * *',
                timezone="America/New_York",
                tasks=RdbTasks(metadata=True, stats=False)
            )
        )

        self.assertEqual(2, len(self.exampleWf._templates))
        self.assertEqual(4, len(self.exampleWf.workflows))
        self.assertEqual({'database': 'db1',
                          'schedule': '*/1 * * * *',
                          'tasks': {'metadata': False, 'stats': True},
                          'type': 'snowflake'}, self.exampleWf.workflows[0].build_yaml())
        self.assertEqual({'database': 'db2',
                          'schedule': '59 23 1,7,14,21 * *',
                          'timezone': 'America/New_York',
                          'tasks': {'metadata': True, 'stats': False},
                          'type': 'snowflake'}, self.exampleWf.workflows[3].build_yaml())
