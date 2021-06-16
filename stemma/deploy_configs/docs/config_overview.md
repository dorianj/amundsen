# Stemma Deployment Configs

This uses a Python-based approach to defininig configurations. Python configs are then turned into either environment variables or YAML configs.

There are two use-cases for this:

## 1. Deployment configs

These are configs that are intended to be passed into Helm charts and into Release. These configs should be provided as environment variables. A `BaseAppConf` has been defined in `config_refs/app_conf/base_app_conf.py` that _should_ contain all a holistic set of all of the potential application configs.
Ideally, as a future development we can segment Stemma features into composable config units and be able to build configurations from both - coded and stored(e.g. persistent store) structures.

```python
class BaseAppConf(StemmaConfGenerator):
    FRONTEND_IMAGE_TAG = 'latest'
    FRONTEND_FLASK_APP_MODULE = 'flaskoidc'
    FRONTEND_APP_CLASS = 'FlaskOIDC'
    METADATA_PROXY_HOST = 'localhost'
    METADATA_PROXY_USER = 'neo4j'
    METADATA_IMAGE_TAG = 'latest'
```

### Creating Customer App Configs

Each individual customer can then override configurations by creating a config object:

```python
from config_refs.app_conf.base_app_conf import BaseAppConf

PreviewConf = BaseAppConf(
    FRONTEND_IMAGE_TAG='Definitely NOT latest'
)
```

By passing in keyword arguments to a config class we can validate that only pre-existing keyword arguments are used and that this sepcific customer does not accidently set variables that do not exist.

Furthermore, we can subclass the `BaseAppConf` to create configs that may be used as
"beta" features:

```python
class NewFeatureConf(BaseAppConf):
    NEWEST_FEATURE = True
    METADATA_IMAGE_TAG = 'Even newer metadata tag'
```

And then use this config with a customer:

```python
DemoConf = NewFeatureConf()
```

### Generating Customer App Evnironment Variables

The `build_configs.py` file will iterate through each of the customers listed in the `./customers/`
directory and will call `.build_envvar()` for each config class that inherits from `BaseAppConf`. These output files are then placed in `./dist/envs/{customer_name}.env`. The output of a file looks like:

```text
FRONTEND_APP_CLASS='FlaskOIDC'
FRONTEND_FLASK_APP_MODULE='flaskoidc'
FRONTEND_IMAGE_TAG='Definitely NOT latest'
METADATA_IMAGE_TAG='latest'
METADATA_PROXY_HOST='localhost'
METADATA_PROXY_USER='neo4j'
```

## 2. Workflows generation from code

### Context

We will need a way to dynamically generate sets of workflows (or DAGs) for each customer's data source. A workflow consists of one or more databuilder actions. For example, for a relational data source we may need to configure items such as:

- The frequency it will run
- Whether or not metadata should be pulled from the information schema
- Whether or not to extract descriptive statistics
- Whether or not to parse the query log
- And more

Each data source can be thought of as having a "workflow" in simple terms. This is not intended to be a comprehensive DAG engine but rather to provide a very simple, configuration-based, approach to orchestrating data builder tasks.
At this point in time, there is not a need to orchestrate workflows across data sources.

### Workflow container

The base data source config is called `BaseDatabuilderWorkflow`.
The `BaseDatabuilderWorkflow` holds multiple sections for each type of workflow that a customer requires and will generate configurations for each populated one.

```python
...

class BaseDatabuilderWorkflow(StemmaConfGenerator):
    rdbWorkflows: List[RdbWorkflows] = []

...
```

The only current implementation is of RdbWorkflows, which allows to produce a series of items for performing the two main stats - metadata extraction & stats.

### Workflow Item

A concrete RdfWorkflowItem's instantiation, therefore, looks like this:
The item itself is a template that will be used to generate an argo workflow execution job for each available source(loaded from secret storage)


```python

        RdbWorkflowItem(
            None,
            schedule='59 23 1,7,14,21 * *',
            timezone="America/New_York",
            secretLocation=PREVIEW_VAULT_SECRETS,
            tasks=RdbTasks(metadata=True, stats=False)
        )

```python

```

### Generating Customer Workflow YAMLs

The `build_configs.py` file will iterate through each of the customers listed in the `./customers/` directory and will call `.build_yaml()` for each config class that inherits from `BaseDatabuilderWorkflow`. This will merge the workflow informatoin stored in the customer configs with the secrets (either in Vault or the local secrets in common). These output files are then placed in `./dist/yamls/{customer_name}.yml`. The output of a file looks like:

```yaml
common:
    clientName: preview
rdbWorkflows:
    workflows:
      - database: '"ca_covid"'
        schedule: '*/1 * * * *'
        secretLocation: secret/data/webapp/config
        tasks:
            metadata: true
            stats: true
        type: snowflake
     - database: SNOWFLAKE_SAMPLE_DATA
        schedule: '*/1 * * * *'
        secretLocation: secret/data/webapp/config
        tasks:
            metadata: true
            stats: true
        type: snowflake
```
