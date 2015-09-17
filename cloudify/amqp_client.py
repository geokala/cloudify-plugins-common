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


import json

import pika
import ssl

from cloudify.utils import get_manager_ip


class AMQPClient(object):

    events_queue_name = 'cloudify-events'
    logs_queue_name = 'cloudify-logs'

    def __init__(self,
                 amqp_host=None,
                 amqp_port=5672,
                 amqp_user='testuser',
                 amqp_pass='testpass',
                 ssl_cert_path=''):
        if amqp_host is None:
            amqp_host = get_manager_ip()

        self.events_queue = None
        self.logs_queue = None

        credentials = pika.credentials.PlainCredentials(
            username=amqp_user,
            password=amqp_pass,
        )

        if ssl_cert_path != '':
            ssl_enabled = True
            ssl_options = {
                'ca_certs': ssl_cert_path,
                'cert_reqs': ssl.CERT_REQUIRED,
            }
        else:
            ssl_enabled = False
            ssl_options = {}

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=amqp_host,
                port=amqp_port,
                credentials=credentials,
                ssl=ssl_enabled,
                ssl_options=ssl_options,
            )
        )
        settings = {
            'auto_delete': True,
            'durable': True,
            'exclusive': False
        }
        self.logs_queue = self.connection.channel()
        self.logs_queue.queue_declare(queue=self.logs_queue_name, **settings)
        self.events_queue = self.connection.channel()
        self.events_queue.queue_declare(queue=self.logs_queue_name, **settings)

    def publish_log(self, log):
        self._publish(log, self.logs_queue_name)

    def publish_event(self, event):
        self._publish(event, self.events_queue_name)

    def close(self):
        self.connection.close()

    def _publish(self, item, queue):
        self.events_queue.basic_publish(exchange='',
                                        routing_key=queue,
                                        body=json.dumps(item))


def create_client(amqp_host=None,
                  amqp_port=5672,
                  amqp_user='testuser',
                  amqp_pass='testpass',
                  ssl_cert_path=''):
    return AMQPClient(
        amqp_host=amqp_host,
        amqp_port=amqp_port,
        amqp_user=amqp_user,
        amqp_pass=amqp_pass,
        ssl_cert_path=ssl_cert_path,
    )
