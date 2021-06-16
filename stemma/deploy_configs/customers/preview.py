from config_builder.app.base import BaseAppConf
from config_builder.workflow.base import BaseDatabuilderWorkflow
from config_builder.workflow.rdb import RdbTasks, RdbWorkflowItem, RdbWorkflows

PreviewConf = BaseAppConf(
    FRONTEND_IMAGE_TAG='Definitely NOT latest'
)


PREVIEW_VAULT_SECRETS = 'secret/data/stemma/snowflake'

DatabuilderWorkflows = BaseDatabuilderWorkflow(
    rdbWorkflows=RdbWorkflows(
        RdbWorkflowItem(
            None,
            schedule='*/1 * * * *',
            secretLocation=PREVIEW_VAULT_SECRETS,
        ),
        RdbWorkflowItem(
            None,
            schedule='59 23 1,7,14,21 * *',
            timezone="America/New_York",
            secretLocation=PREVIEW_VAULT_SECRETS,
            tasks=RdbTasks(metadata=True, stats=False)
        )
    )
)
