########
# Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
############

import os
import unittest


class TemporaryWorkdirSet(object):
    """
        Context for temporarily overriding the workdir envvar.
        This is intended to avoid unexpected contamination of other tests.
    """
    def __init__(self, value):
        self.envvar = 'CELERY_WORK_DIR'
        self.value = value

    def __enter__(self):
        try:
            self.oldvalue = os.environ[self.envvar]
        except KeyError:
            self.oldvalue = None

        os.environ[self.envvar] = self.value

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.oldvalue is not None:
            os.environ[self.envvar] = self.oldvalue
        return False


# These tests need to be performed by setting os env var CELERY_WORK_DIR
# They must point to files in the cloudify/tests/resources dir
# This is ugly, but unavoidable as the config gets set on import and doing
# that is probably unavoidable if this is to continue to work with celery.
class TestBrokerConfigBase(unittest.TestCase):

    expected_default = {
        'broker_ssl_enabled': False,
        'broker_cert_path': '',
        'broker_username': 'guest',
        'broker_password': 'guest',
        'broker_hostname': 'localhost',
    }

    def _get_broker_values(self, config):
        return {
            'broker_ssl_enabled': config.broker_ssl_enabled,
            'broker_cert_path': config.broker_cert_path,
            'broker_username': config.broker_username,
            'broker_password': config.broker_password,
            'broker_hostname': config.broker_hostname,
        }

    def _get_test_config_path(self, config_name):
        tests_path = os.path.dirname(__file__)
        tests_resource_path = os.path.join(
            tests_path,
            'resources',
        )
        return os.path.join(
            tests_resource_path,
            config_name,
        )
