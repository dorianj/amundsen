import importlib
import os
from amundsen_common.stemma.secrets.manager.base import BaseSecretManager
from amundsen_common.stemma.secrets.manager.environ import EnvironSecretManager
from typing import Dict, Optional, Any


# Allows for swapping out the underlying secret manager in the future
def get_secrets_manager(key: Optional[str] = None, options: Dict[str, Any] = {}) -> BaseSecretManager:
    secret_mgr_env = os.environ.get('SECRET_MANAGER_CLASS')
    if secret_mgr_env:
        secret_mgr_split = secret_mgr_env.split('.')  # type: ignore
        secret_mgr_pkg = '.'.join(secret_mgr_split[:-1])
        secret_mgr_class = secret_mgr_split[-1]

        secret_mgr = getattr(importlib.import_module(secret_mgr_pkg), secret_mgr_class)(key, options)
    else:
        secret_mgr = EnvironSecretManager(key, options)
    return secret_mgr
