import os
from pathlib import Path

import yaml

from charmhelpers.core import hookenv
from charms.reactive import set_flag, clear_flag
from charms.reactive import when, when_not, when_any

from charms import layer


@when('charm.kubeflow-tf-job-operator.started')
def charm_ready():
    layer.status.active('')


@when_any('layer.docker-resource.tf-operator-image.changed',
          'config.changed')
def update_image():
    clear_flag('charm.kubeflow-tf-job-operator.started')


@when('layer.docker-resource.tf-operator-image.available')
@when_not('charm.kubeflow-tf-job-operator.started')
def start_charm():
    layer.status.maintenance('configuring container')

    config = hookenv.config()
    conf_dir = '/etc/tf_operator'
    conf_file = 'controller_config_file.yaml'
    image_info = layer.docker_resource.get_info('tf-operator-image')

    crd = yaml.load(Path(f"files/crd-{config['job-version']}.yaml").read_text())

    if config['job-version'] == 'v1alpha2':
        command = [
            '/opt/kubeflow/tf-operator.v2',
            '--alsologtostderr',
            '-v=1',
        ]
    else:
        command = [
            '/opt/mlkube/tf-operator',
            '--controller-config-file={}/{}'.format(conf_dir, conf_file),
            '--alsologtostderr',
            '-v=1',
        ]

    layer.caas_base.pod_spec_set({
        'containers': [
            {
                'name': 'tf-job-operator',
                'imageDetails': {
                    'imagePath': image_info.registry_path,
                    'username': image_info.username,
                    'password': image_info.password,
                },
                'command': command,
                'ports': [
                    {
                        'name': 'dummy',
                        'containerPort': 9999,
                    },
                ],
                'config': {
                    'MY_POD_NAMESPACE': os.environ['JUJU_MODEL_NAME'],
                    'MY_POD_NAME': hookenv.service_name(),
                },
                'files': [
                    {
                        'name': 'configs',
                        'mountPath': conf_dir,
                        'files': {
                            conf_file: yaml.dump({
                                'grpcServerFilePath': (
                                    '/opt/mlkube/grpc_tensorflow_server/'
                                    'grpc_tensorflow_server.py'
                                ),
                            }),
                        },
                    },
                ],
            },
        ],
        # Backwards compatibility for juju < 2.5.4
        'customResourceDefinition': [{
            'group': crd['spec']['group'],
            'version': crd['spec']['version'],
            'scope': crd['spec']['scope'],
            'kind': crd['spec']['names']['kind'],
            'validation': crd['spec']['validation']['openAPIV3Schema']['properties']['spec'],
        }],
        'customResourceDefinitions': {
            crd['metadata']['name']: crd['spec'],
        },
    })

    layer.status.maintenance('creating container')
    set_flag('charm.kubeflow-tf-job-operator.started')


@when('charm.kubeflow-tf-job-operator.started')
@when('config.changed.job-version')
def restart_container():
    clear_flag('charm.kubeflow-tf-job-operator.started')
    clear_flag('config.changed.job-version')
