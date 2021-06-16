import importlib
import sys
from os.path import basename, dirname, join, realpath
from pathlib import Path
from typing import Any, Dict, List

import yaml

from config_builder.app.base import BaseAppConf
from config_builder.workflow.base import BaseDatabuilderWorkflow


def _prepare_config_dir(base: str, target: str) -> str:
    target_path = join(base, target)
    Path(target_path).mkdir(parents=True, exist_ok=True)
    return target_path


def _escape_v(v: str) -> str:
    """Wrap envvar values with quotes when not provided"""
    if v.startswith('"') and v.endswith('"'):
        pass
    elif v.startswith("'") and v.endswith("'"):
        pass
    else:
        v = f"'{v}'"
    return v


def write_env(envvars: List[Dict], target_file: str) -> None:
    envvar_str = '\n'.join([f'{i["key"]}={_escape_v(i["value"])}' for i in envvars])
    print(f'Creating env vars: {target_file}', flush=True)
    with open(target_file, 'w+') as f:
        f.write(envvar_str)


def write_yaml(yaml_confs: Dict[str, Any], target_file: str) -> None:
    print(f'Creating yaml file: {target_file}', flush=True)
    with open(target_file, 'w+') as f:
        f.write(yaml.dump(yaml_confs))


if __name__ == '__main__':

    target_customer = None
    if len(sys.argv) > 1:
        print(f'Selecting single customer: {sys.argv[1]}')
        target_customer = sys.argv[1]

    DEPLOY_CONFIGS_PATH = dirname(realpath(__file__))

    PATH_ENVS = _prepare_config_dir(DEPLOY_CONFIGS_PATH, 'dist/envs')
    PATH_YAML = _prepare_config_dir(DEPLOY_CONFIGS_PATH, 'dist/yamls')
    PATH_CUSTOMERS = _prepare_config_dir(DEPLOY_CONFIGS_PATH, 'customers')

    customer_configs = [
        p.name[:-3]
        for p in Path(PATH_CUSTOMERS).glob('*.py')
        if p.is_file() and not p.name.endswith('__init__.py')
    ]

    # For side effect only
    customers = __import__('customers')
    for customer in customer_configs:
        if not target_customer or target_customer == customer:
            print(f'Processing configuration for customer: {customer}', flush=True)
            customer_conf = importlib.import_module(
                '.'.join([basename(PATH_CUSTOMERS), customer])
            )
            this_conf = None
            for potential_conf in dir(customer_conf):
                cls_obs = getattr(customer_conf, potential_conf)
                if isinstance(cls_obs, BaseAppConf):
                    write_env(cls_obs.build_env(), join(PATH_ENVS, f'{customer}.env'))
                    break

                if isinstance(cls_obs, BaseDatabuilderWorkflow):
                    data_source_yaml = cls_obs.build_yaml()
                    # Add customer namecommon:s
                    data_source_yaml['common'] = {'customerName': customer}
                    write_yaml(data_source_yaml, join(PATH_YAML, f'{customer}.yml'))
