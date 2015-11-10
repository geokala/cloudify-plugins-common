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
import unittest

from mock import patch

import cloudify


class TestAMQPClient(unittest.TestCase):

    @patch('cloudify.amqp_client.get_manager_ip')
    @patch('cloudify.amqp_client.pika')
    def test_amqp_client_uses_default_credentials(self,
                                                  mock_pika,
                                                  mock_get_ip):
        cloudify.amqp_client.AMQPClient()

        mock_pika.credentials.PlainCredentials.assert_called_once_with(
            username='guest',
            password='guest',
        )

    @patch('cloudify.amqp_client.get_manager_ip')
    @patch('cloudify.amqp_client.pika')
    def test_amqp_client_uses_provided_credentials(self,
                                                   mock_pika,
                                                   mock_get_ip):
        username = 'notauser'
        password = 'secretword'
        cloudify.amqp_client.AMQPClient(
            amqp_user=username,
            amqp_pass=password,
        )

        mock_pika.credentials.PlainCredentials.assert_called_once_with(
            username=username,
            password=password,
        )

    @patch('cloudify.amqp_client.get_manager_ip')
    @patch('cloudify.amqp_client.pika')
    def test_amqp_client_ssl_default_setting(self,
                                             mock_pika,
                                             mock_get_ip):
        cloudify.amqp_client.AMQPClient()

        mock_pika.ConnectionParameters.assert_called_once_with(
            host=mock_get_ip.return_value,
            port=5672,
            credentials=mock_pika.credentials.PlainCredentials.return_value,
            ssl=False,
            ssl_options={},
        )

    @patch('cloudify.amqp_client.get_manager_ip')
    @patch('cloudify.amqp_client.pika')
    def test_amqp_client_ssl_enabled(self,
                                     mock_pika,
                                     mock_get_ip):
        cert_path = '/not/a/real/cert.pem'
        cloudify.amqp_client.AMQPClient(
            ssl_enabled=True,
            ssl_cert_path=cert_path,
        )

        mock_pika.ConnectionParameters.assert_called_once_with(
            host=mock_get_ip.return_value,
            port=5671,
            credentials=mock_pika.credentials.PlainCredentials.return_value,
            ssl=True,
            ssl_options={
                'ca_certs': cert_path,
                'cert_reqs': ssl.CERT_REQUIRED,
            },
        )
