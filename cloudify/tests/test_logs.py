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

import unittest

from mock import patch, PropertyMock

import cloudify


class TestLogs(unittest.TestCase):

    @patch('cloudify.logs.create_event_message_prefix',
           return_value='expected')
    @patch('cloudify.logs.sys.stdout')
    @patch('cloudify.logs.populate_base_item')
    def test_stdout_event_out(self,
                              mock_populate_item,
                              mock_stdout,
                              mock_message_prefix):
        cloudify.logs.stdout_event_out(
            event='test',
            ctx=None,
        )

        mock_stdout.write.assert_called_once_with('expected\n')

    @patch('cloudify.logs.create_event_message_prefix',
           return_value='expected')
    @patch('cloudify.logs.sys.stdout')
    @patch('cloudify.logs.populate_base_item')
    def test_stdout_log_out(self,
                            mock_populate_item,
                            mock_stdout,
                            mock_message_prefix):
        cloudify.logs.stdout_log_out(
            log='test',
            ctx=None,
        )

        mock_stdout.write.assert_called_once_with('expected\n')

    @patch('cloudify.logs.broker_config')
    @patch('cloudify.logs.create_client')
    @patch('cloudify.logs.populate_base_item')
    def test_amqp_event_out(self,
                            mock_populate_item,
                            mock_create_client,
                            mock_broker_config):
        cloudify.logs.amqp_event_out(
            event='expected',
            ctx='context',
        )

        mock_create_client.return_value.publish_event.assert_called_once_with(
            'expected',
        )

        delattr(cloudify.logs.clients, 'amqp_client')

    @patch('cloudify.logs.broker_config')
    @patch('cloudify.logs.create_client')
    @patch('cloudify.logs.populate_base_item')
    def test_amqp_log_out(self,
                          mock_populate_item,
                          mock_create_client,
                          mock_broker_config):
        cloudify.logs.amqp_log_out(
            log='expected',
            ctx='context',
        )

        mock_create_client.return_value.publish_log.assert_called_once_with(
            'expected',
        )

        delattr(cloudify.logs.clients, 'amqp_client')

    @patch('cloudify.logs.create_client')
    @patch('cloudify.logs.broker_config')
    def test_create_client(self,
                           mock_broker_config,
                           mock_create_client):
        broker_hostname = 'somehost'
        broker_user = 'guest'
        broker_pass = 'secret'
        broker_ssl_enabled = True
        broker_ssl_cert_path = 'path'

        type(mock_broker_config).broker_hostname = PropertyMock(
            return_value=broker_hostname
        )
        type(mock_broker_config).broker_username = PropertyMock(
            return_value=broker_user,
        )
        type(mock_broker_config).broker_password = PropertyMock(
            return_value=broker_pass,
        )
        type(mock_broker_config).broker_ssl_enabled = PropertyMock(
            return_value=broker_ssl_enabled
        )
        type(mock_broker_config).broker_cert_path = PropertyMock(
            return_value=broker_ssl_cert_path
        )

        cloudify.logs._amqp_client(ctx='context')

        mock_create_client.assert_called_once_with(
            amqp_host=broker_hostname,
            amqp_user=broker_user,
            amqp_pass=broker_pass,
            ssl_enabled=broker_ssl_enabled,
            ssl_cert_path=broker_ssl_cert_path,
        )

        delattr(cloudify.logs.clients, 'amqp_client')
