########
# Copyright (c) 2013 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

import logging
import ssl
import unittest

from cloudify.utils import setup_logger
from cloudify.utils import LocalCommandRunner
from cloudify.utils import internal
from cloudify.exceptions import CommandExecutionException


class LocalCommandRunnerTest(unittest.TestCase):

    runner = None

    @classmethod
    def setUpClass(cls):
        cls.logger = setup_logger(cls.__name__)
        cls.logger.setLevel(logging.DEBUG)
        cls.runner = LocalCommandRunner(
            logger=cls.logger)

    def test_run_command_success(self):
        response = self.runner.run('echo Hello')
        self.assertEqual('Hello', response.std_out)
        self.assertEqual(0, response.return_code)
        self.assertEqual('', response.std_err)

    def test_run_command_error(self):
        try:
            self.runner.run('/bin/sh -c bad')
            self.fail('Expected CommandExecutionException due to Bad command')
        except CommandExecutionException as e:
            self.assertTrue(1, e.code)

    def test_run_command_with_env(self):
        response = self.runner.run('env',
                                   execution_env={'TEST_KEY': 'TEST_VALUE'})
        self.assertTrue('TEST_KEY=TEST_VALUE' in response.std_out)


class FakeAgent(object):
    def __init__(self, broker_user=None, broker_pass=None):
        if broker_user is not None:
            self.broker_user = broker_user
        if broker_pass is not None:
            self.broker_pass = broker_pass


class BrokerSecurityMethodsTest(unittest.TestCase):
    def test_get_broker_ssl_options_with_ssl_enabled(self):
        cert_path = '/not/real/cert.pem'
        _, options = internal.get_broker_ssl_and_port(
            ssl_enabled=True,
            cert_path=cert_path,
        )

        expected_options = {
            'ca_certs': cert_path,
            'cert_reqs': ssl.CERT_REQUIRED,
        }

        self.assertEqual(
            expected_options,
            options,
        )

    def test_get_broker_port_with_ssl_enabled(self):
        port, _ = internal.get_broker_ssl_and_port(
            ssl_enabled=True,
            cert_path='something',
        )

        self.assertEqual(
            5671,
            port,
        )

    def test_get_broker_ssl_options_with_ssl_disabled(self):
        _, options = internal.get_broker_ssl_and_port(
            ssl_enabled=False,
            cert_path='',
        )

        self.assertEqual(
            {},
            options,
        )

    def test_get_broker_port_with_ssl_disabled(self):
        port, _ = internal.get_broker_ssl_and_port(
            ssl_enabled=False,
            cert_path='',
        )

        self.assertEqual(
            5672,
            port,
        )

    def test_get_broker_credentials_default_with_missing_broker_user(self):
        fake_agent = FakeAgent(
            broker_pass='something',
        )

        result = internal.get_broker_credentials(fake_agent)

        expected = (
            'guest',
            'guest',
        )

        self.assertEqual(
            expected,
            result,
        )

    def test_get_broker_credentials_default_with_missing_broker_pass(self):
        fake_agent = FakeAgent(
            broker_user='something',
        )

        result = internal.get_broker_credentials(fake_agent)

        expected = (
            'guest',
            'guest',
        )

        self.assertEqual(
            expected,
            result,
        )

    def test_get_broker_credentials_with_provided_credentials(self):
        fake_agent = FakeAgent(
            broker_user='myuser',
            broker_pass='mypass',
        )

        result = internal.get_broker_credentials(fake_agent)

        expected = (
            'myuser',
            'mypass',
        )

        self.assertEqual(
            expected,
            result,
        )
