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

from cloudify.tests.test_broker_config_base import TestBrokerConfigBase


# These tests need to be performed by setting os env var CELERY_WORK_DIR
# They must point to files in the cloudify/tests/resources dir
# This is ugly, but unavoidable as the config gets set on import and doing
# that is probably unavoidable if this is to continue to work with celery.
# Note that this is split into multiple modules as importing the same module
# successfully multiple times causes unusable test results.
class TestBrokerConfigDefaults(TestBrokerConfigBase):

    def test_amqp_client_uses_defaults_without_workdir(self):
        import cloudify.broker_config as config

        values = self._get_broker_values(config)

        self.assertEqual(
            values,
            self.expected_default,
        )

    def test_amqp_client_defaults_derived_url(self):
        import cloudify.broker_config as config

        self.assertEqual(
            'amqp://guest:guest@localhost:5672',
            config.BROKER_URL,
        )
