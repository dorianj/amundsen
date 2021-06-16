import copy
from typing import List, Optional

from amundsen_common.stemma.secrets import get_secrets_manager
from amundsen_common.stemma.secrets.manager.base import BaseSecretManager

from config_builder.generator.stemma_conf import StemmaConfGenerator


class RdbTasks(StemmaConfGenerator):
    """
    Data class enumerating the possible tasks for RDB extraction
    Default state of tasks is off (false).
    """
    metadata: bool = False
    stats: bool = False


class RdbWorkflowItem(StemmaConfGenerator):
    """
    A Workflow job, holding credentials, schedule and a task description to be executed.
    """
    schedule: Optional[str] = None
    timezone: Optional[str] = None
    type: Optional[str] = None
    database: Optional[str] = None
    secretLocation: Optional[str] = None
    tasks: RdbTasks = RdbTasks()

    def __init__(self, sm: Optional[BaseSecretManager], **kwargs) -> None:  # type: ignore
        super().__init__(**kwargs)
        self._secrets_manager = sm if sm is not None else get_secrets_manager()
        self.type = self._secrets_manager.secrets['TYPE']

    def generate_executions(self) -> List:
        workflows = []
        for db in self._secrets_manager.secrets['DATABASES']:
            wf_copy = copy.deepcopy(self)
            wf_copy.database = db['NAME']
            wf_copy.tasks.metadata = db.get('METADATA', wf_copy.tasks.metadata)
            wf_copy.tasks.stats = db.get('STATS', wf_copy.tasks.stats)
            workflows.append(wf_copy)
        return workflows


class RdbWorkflows(StemmaConfGenerator):
    _templates: List[RdbWorkflowItem] = []
    workflows: List[RdbWorkflowItem] = []

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        super().__init__(**kwargs)
        self._templates = list(args)
        for wf_item in self._templates:
            self.workflows.extend(wf_item.generate_executions())
