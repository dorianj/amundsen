# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import os

from metadata_service import create_app

'''
  Entry point to flask.
'''

# Uses the STEMMA Specific configurations
application = create_app(
    config_module_class=os.getenv('METADATA_SVC_CONFIG_MODULE_CLASS')
    or 'metadata_service.stemma.config.StemmaConfig')

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=5002)
