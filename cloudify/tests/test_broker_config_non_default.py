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

import ssl

from cloudify.tests.test_broker_config_base import (
    TestBrokerConfigBase,
#    TemporaryWorkdirSet,
)


# These tests need to be performed by setting os env var CELERY_WORK_DIR
# They must point to files in the cloudify/tests/resources dir
# This is ugly, but unavoidable as the config gets set on import and doing
# that is probably unavoidable if this is to continue to work with celery.
# Note that this is split into multiple modules as importing the same module
# successfully multiple times causes unusable test results.
class TestBrokerConfigNonDefault(TestBrokerConfigBase):

    def setUp(self):
        config_path = self._get_test_config_path(
            'test_broker_config',
        )
        # override = TemporaryWorkdirSet(config_path)
        # with override:

        import os
        os.environ['CELERY_WORK_DIR'] = config_path
        import cloudify.broker_config as config
        self.config = config

    def test_amqp_client_uses_overrides_from_json(self):
        expected_new_values = {
            'broker_ssl_enabled': True,
            'broker_cert_path': 'thispath',
            'broker_username': 'nothere',
            'broker_password': 'everywhere',
            'broker_hostname': 'newhost',
        }

        values = self._get_broker_values(self.config)

        self.assertEqual(
            values,
            expected_new_values,
        )

    def test_amqp_client_overridden_derived_url(self):
        self.assertEqual(
            'amqp://nothere:everywhere@newhost:5671',
            self.config.BROKER_URL,
        )

    def test_amqp_client_overridden_derived_ssl_settings(self):
        expected_ssl_settings = {
            'ca_certs': 'thispath',
            'cert_reqs': ssl.CERT_REQUIRED,
        }

        self.assertEqual(
            expected_ssl_settings,
            self.config.BROKER_USE_SSL,
        )
