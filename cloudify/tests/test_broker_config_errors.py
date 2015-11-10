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

from cloudify.tests.test_broker_config_base import (
    TestBrokerConfigBase,
    TemporaryWorkdirSet,
)


# These tests need to be performed by setting os env var CELERY_WORK_DIR
# They must point to files in the cloudify/tests/resources dir
# This is ugly, but unavoidable as the config gets set on import and doing
# that is probably unavoidable if this is to continue to work with celery.
# Note that this is split into multiple modules as importing the same module
# successfully multiple times causes unusable test results.
class TestBrokerConfigErrors(TestBrokerConfigBase):

    def test_amqp_client_error_with_empty_broker_config(self):
        empty_config_path = self._get_test_config_path(
            'empty_broker_config',
        )
        # override = TemporaryWorkdirSet(empty_config_path)
        import os
        os.environ['CELERY_WORK_DIR'] = empty_config_path

        try:
            # with override:
            import cloudify.broker_config  # noqa
            raise AssertionError(cloudify.broker_config.workdir_path)
            raise AssertionError(
                'Expected ValueError with empty broker config.',
            )
        except ValueError as err:
            self.assertIn(
                'No JSON object could be decoded',
                err.message,
            )

    def test_amqp_client_exception_with_missing_config(self):
        missing_config_path = self._get_test_config_path(
            'this_directory_should_not_exist_please_delete',
        )
        # override = TemporaryWorkdirSet(missing_config_path)
        import os
        os.environ['CELERY_WORK_DIR'] = missing_config_path

        try:
            # with override:
            import cloudify.broker_config  # noqa
            raise AssertionError(
                'Expected IOError with missing broker config.',
            )
        except IOError as err:
            self.assertIn(
                'No such file or directory',
                err.strerror,
            )
