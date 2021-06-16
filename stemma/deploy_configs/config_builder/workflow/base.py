from typing import List

from config_builder.generator.stemma_conf import StemmaConfGenerator
from config_builder.workflow.rdb import RdbWorkflows


class BaseDatabuilderWorkflow(StemmaConfGenerator):
    rdbWorkflows: List[RdbWorkflows] = []
