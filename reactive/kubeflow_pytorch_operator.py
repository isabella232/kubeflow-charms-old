import os
import yaml

from charmhelpers.core import hookenv
from charms.reactive import set_flag, clear_flag
from charms.reactive import when, when_not

from charms import layer


@when('charm.kubeflow-pytorch-operator.started')
def charm_ready():
    layer.status.active('')


@when('config.changed')
def update_config():
    clear_flag('charm.kubeflow-pytorch-operator.started')


@when('layer.docker-resource.pytorch-operator-image.changed')
def update_image():
    clear_flag('charm.kubeflow-pytorch-operator.started')


@when('layer.docker-resource.pytorch-operator-image.available')
@when_not('charm.kubeflow-pytorch-operator.started')
def start_charm():
    layer.status.maintenance('configuring container')

    config = hookenv.config()
    conf_dir = '/etc/config'
    conf_file = 'controller_config_file.yaml'
    conf_path = '/'.join([conf_dir, conf_file])
    image_info = layer.docker_resource.get_info('pytorch-operator-image')

    conf_data = {}
    if config['pytorch-default-image']:
        conf_data['pytorchImage'] = config['pytorch-default-image']

    layer.caas_base.pod_spec_set({
        'containers': [
            {
                'name': 'pytorch-operator',
                'imageDetails': {
                    'imagePath': image_info.registry_path,
                    'username': image_info.username,
                    'password': image_info.password,
                },
                'command': [
                    '/pytorch-operator',
                    '--controller-config-file={}'.format(conf_path),
                    '--alsologtostderr',
                    '-v=1',
                ],
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
                            conf_file: yaml.dump(conf_data),
                        },
                    },
                ],
            },
        ],
        'customResourceDefinition': [
            {
                'group': 'kubeflow.org',
                'version': 'v1alpha1',
                'scope': 'Namespaced',
                'kind': 'PyTorchJob',
                'validation': {}
            },
        ],
    })

    layer.status.maintenance('creating container')
    set_flag('charm.kubeflow-pytorch-operator.started')
