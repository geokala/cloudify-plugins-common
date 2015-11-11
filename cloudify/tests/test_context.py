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
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

import os
from os.path import dirname

import testtools

from cloudify import constants
from cloudify import context
from cloudify import exceptions
from cloudify.utils import create_temp_folder
from cloudify.decorators import operation
from cloudify.workflows import local

import cloudify.tests as tests_path
from cloudify.test_utils import workflow_test


class CloudifyContextTest(testtools.TestCase):
    file_server_process = None

    @classmethod
    def setUpClass(cls):

        resources_path = os.path.join(dirname(tests_path.__file__),
                                      "resources")

        from cloudify.tests.file_server import FileServer
        from cloudify.tests.file_server import PORT

        cls.file_server_process = FileServer(resources_path)
        cls.file_server_process.start()

        os.environ[constants.MANAGER_FILE_SERVER_BLUEPRINTS_ROOT_URL_KEY] \
            = "http://localhost:{0}".format(PORT)
        os.environ[constants.MANAGER_FILE_SERVER_URL_KEY] = \
            "http://localhost:{0}".format(PORT)
        cls.context = context.CloudifyContext({'blueprint_id': ''})

    @classmethod
    def tearDownClass(cls):
        cls.file_server_process.stop()

    def test_get_resource(self):
        resource = self.context.get_resource(resource_path='for_test.log')
        self.assertIsNotNone(resource)

    def test_download_resource(self):
        resource_path = self.context.download_resource(
            resource_path='for_test.log')
        self.assertIsNotNone(resource_path)
        self.assertTrue(os.path.exists(resource_path))

    def test_download_resource_to_specific_file(self):
        target_path = "{0}/for_test_custom.log".format(create_temp_folder())
        resource_path = self.context.download_resource(
            resource_path='for_test.log',
            target_path=target_path)
        self.assertEqual(target_path, resource_path)
        self.assertTrue(os.path.exists(resource_path))

    def test_download_resource_to_non_writable_location(self):
        self.assertRaises(IOError, self.context.download_resource,
                          'for_test.log',
                          '/non-existing-folder')

    def test_get_non_existing_resource(self):
        self.assertRaises(exceptions.HttpException, self.context.get_resource,
                          'non_existing.log')

    def test_ctx_instance_in_relationship(self):
        ctx = context.CloudifyContext({
            'node_id': 'node-instance-id',
            'related': {
                'node_id': 'related-instance-id',
                'is_target': True
            },
            'relationships': ['related-instance-id']
        })
        self.assertEqual('node-instance-id', ctx.source.instance.id)
        self.assertEqual('related-instance-id', ctx.target.instance.id)
        e = self.assertRaises(exceptions.NonRecoverableError,
                              lambda: ctx.node)
        self.assertIn('ctx.node/ctx.instance can only be used in a '
                      'node-instance context but used in a '
                      'relationship-instance context.', str(e))
        e = self.assertRaises(exceptions.NonRecoverableError,
                              lambda: ctx.instance)
        self.assertIn('ctx.node/ctx.instance can only be used in a '
                      'node-instance context but used in a '
                      'relationship-instance context.', str(e))

    def test_source_target_not_in_relationship(self):
        ctx = context.CloudifyContext({})
        e = self.assertRaises(exceptions.NonRecoverableError,
                              lambda: ctx.source)
        self.assertIn('ctx.source/ctx.target can only be used in a '
                      'relationship-instance context but used in a '
                      'deployment context.', str(e))
        e = self.assertRaises(exceptions.NonRecoverableError,
                              lambda: ctx.target)
        self.assertIn('ctx.source/ctx.target can only be used in a '
                      'relationship-instance context but used in a '
                      'deployment context.', str(e))

    def test_ctx_type(self):
        ctx = context.CloudifyContext({})
        self.assertEqual(context.DEPLOYMENT, ctx.type)
        ctx = context.CloudifyContext({'node_id': 'node-instance-id'})
        self.assertEqual(context.NODE_INSTANCE, ctx.type)
        ctx = context.CloudifyContext({
            'node_id': 'node-instance-id',
            'related': {
                'node_id': 'related-instance-id',
                'is_target': True
            },
            'relationships': ['related-instance-id']
        })
        self.assertEqual(context.RELATIONSHIP_INSTANCE, ctx.type)


class NodeContextTests(testtools.TestCase):

    test_blueprint_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "resources/blueprints/test-context-node.yaml")

    @workflow_test(blueprint_path=test_blueprint_path,
                   resources_to_copy=[
                       'resources/blueprints/execute_operation_workflow.yaml'])
    def test_node_type(self, cfy_local):
        cfy_local.execute('execute_operation', parameters={
            'operation': 'test.interface.create',
            'nodes': ['node1', 'node2'],
            'testing': 'test_node_type'})

        expected = {
            'node1': ['test.node1.type', ['test.node1.type']],
            'node2': [
                'test.node2.type',
                ['test.node1.type', 'test.node2.type']]}

        for node in ['node1', 'node2']:
            instance = cfy_local.storage.get_node_instances(node_id=node)[0]
            self.assertEqual(expected[node][0],
                             instance.runtime_properties['type'])
            self.assertEqual(expected[node][1],
                             instance.runtime_properties['type_hierarchy'])


class BootstrapContextTests(testtools.TestCase):
    def test_broker_security_username_is_in_agent(self):
        agent = context.BootstrapContext.CloudifyAgent
        self.assertIn(
            'broker_user',
            dir(agent),
        )

    def test_broker_security_password_is_in_agent(self):
        agent = context.BootstrapContext.CloudifyAgent
        self.assertIn(
            'broker_pass',
            dir(agent),
        )

    def test_broker_security_ssl_flag_is_in_agent(self):
        agent = context.BootstrapContext.CloudifyAgent
        self.assertIn(
            'broker_ssl_enabled',
            dir(agent),
        )

    def test_broker_security_ssl_cert_is_in_agent(self):
        agent = context.BootstrapContext.CloudifyAgent
        self.assertIn(
            'broker_ssl_cert',
            dir(agent),
        )


class GetResourceTemplateTests(testtools.TestCase):

    def __init__(self, *args, **kwargs):
        super(GetResourceTemplateTests, self).__init__(*args, **kwargs)
        self.blueprint_resources_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "resources/blueprints/resources")
        self.blueprint_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "resources/blueprints/test-get-resource-template.yaml")

    def setUp(self):
        super(GetResourceTemplateTests, self).setUp()

    def _assert_rendering(self, env, download,
                          rendered, should_fail_rendering):
        instance = env.storage.get_node_instances(node_id='node1')[0]
        resource = instance.runtime_properties['resource']
        if not should_fail_rendering:
            if download:
                with open(resource, 'r') as f:
                    rendered_resource = f.read()
            else:
                rendered_resource = resource

            if rendered == 'normal':
                expected_resource_path = \
                    os.path.join(self.blueprint_resources_path,
                                 'rendered_template.conf')
            elif rendered == 'extended':
                expected_resource_path = \
                    os.path.join(self.blueprint_resources_path,
                                 'extended_rendered_template.conf')
            else:
                expected_resource_path = \
                    os.path.join(self.blueprint_resources_path,
                                 'for_template_rendering_tests.conf')

            with open(expected_resource_path, 'r') as f:
                expected = f.read()
            self.assertEqual(expected, rendered_resource)
        else:
            self.assertEqual('failed', resource)

    def _generic_get_download_template_test(self,
                                            parameters,
                                            download=False,
                                            rendered='normal',
                                            should_fail_rendering=False):
        env = local.init_env(self.blueprint_path)
        updated_params = {'nodes': ['node1']}
        updated_params.update(parameters)
        env.execute('execute_operation',
                    parameters=updated_params)
        self._assert_rendering(env, download,
                               rendered, should_fail_rendering)

    def test_get_resource_template_with_ctx(self):
        self._generic_get_download_template_test({
            'operation': 'get_template',
            'testing': 'get_resource_with_ctx'
        }, rendered='false', should_fail_rendering=True)

    def test_get_resource_no_template(self):
        self._generic_get_download_template_test({
            'operation': 'get_template',
            'testing': 'get_resource_no_template'
        })

    def test_get_resource_empty_template_variables(self):
        self._generic_get_download_template_test({
            'operation': 'get_template',
            'testing': 'get_resource_empty_template'
        })

    def test_get_resource(self):
        self._generic_get_download_template_test({
            'operation': 'get_template',
            'testing': 'get_resource'
        }, rendered='extended')

    def test_download_resource_template_with_ctx(self):
        self._generic_get_download_template_test(
            dict(operation='download_template',
                 testing='download_resource_with_ctx'),
            download=True,
            rendered='false',
            should_fail_rendering=True)

    def test_download_resource_no_template(self):
        self._generic_get_download_template_test(
            dict(operation='download_template',
                 testing='download_resource_no_template'),
            download=True)

    def test_download_resource_empty_template_variables(self):
        self._generic_get_download_template_test(
            dict(operation='download_template',
                 testing='download_resource_empty_template'),
            download=True)

    def test_download_resource(self):
        self._generic_get_download_template_test(
            dict(operation='download_template',
                 testing='download_resource'),
            download=True,
            rendered='extended')


@operation
def get_template(ctx, testing, **_):

    resource = 'empty'
    rendering_tests_demo_conf = 'resources/for_template_rendering_tests.conf'

    if testing == 'get_resource_with_ctx':
        try:
            resource = ctx.get_resource_and_render(
                rendering_tests_demo_conf,
                template_variables={'ctx': ctx})
        except exceptions.NonRecoverableError:
            print 'caught expected exception'
            resource = 'failed'

    if testing == 'get_resource_no_template':
        resource = ctx.get_resource_and_render(rendering_tests_demo_conf)

    if testing == 'get_resource_empty_template':
        resource = ctx.get_resource_and_render(rendering_tests_demo_conf,
                                               template_variables={})

    if testing == 'get_resource':
        resource = ctx.get_resource_and_render(
            rendering_tests_demo_conf,
            template_variables={'key': 'value'})

    ctx.instance.runtime_properties['resource'] = resource


@operation
def download_template(ctx, testing, **_):

    resource = 'empty'
    rendering_tests_demo_conf = 'resources/for_template_rendering_tests.conf'

    if testing == 'download_resource_with_ctx':
        try:
            resource = ctx.download_resource_and_render(
                rendering_tests_demo_conf,
                template_variables={'ctx': ctx})
        except exceptions.NonRecoverableError:
            print 'caught expected exception'
            resource = 'failed'

    if testing == 'download_resource_no_template':
        resource = ctx.download_resource_and_render(
            rendering_tests_demo_conf)

    if testing == 'download_resource_empty_template':
        resource = ctx.download_resource_and_render(
            rendering_tests_demo_conf,
            template_variables={})

    if testing == 'download_resource':
        resource = ctx.download_resource_and_render(
            rendering_tests_demo_conf,
            template_variables={'key': 'value'})

    ctx.instance.runtime_properties['resource'] = resource


@operation
def get_node_type(ctx, **kwargs):
    ctx.instance.runtime_properties['type'] = ctx.node.type
    ctx.instance.runtime_properties['type_hierarchy'] = ctx.node.type_hierarchy
