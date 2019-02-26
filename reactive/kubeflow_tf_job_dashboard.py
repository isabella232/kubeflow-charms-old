import yaml
from charmhelpers.core import hookenv
from charms import layer
from charms.reactive import set_flag, clear_flag
from charms.reactive import when, when_not


@when('charm.kubeflow-tf-job-dashboard.started')
def charm_ready():
    layer.status.active('')


@when('layer.docker-resource.tf-operator-image.changed')
def update_image():
    clear_flag('charm.kubeflow-tf-job-dashboard.started')


@when('layer.docker-resource.tf-operator-image.available')
@when_not('charm.kubeflow-tf-job-dashboard.started')
def start_charm():
    layer.status.maintenance('configuring container')

    image_info = layer.docker_resource.get_info('tf-operator-image')
    port = 8080

    layer.caas_base.pod_spec_set({
        'service': {
            'annotations': {
                'getambassador.io/config': yaml.dump_all([
                    {
                        'apiVersion': 'ambassador/v0',
                        'kind':  'Mapping',
                        'name':  'tf_dashboard',
                        'prefix': '/tfjobs/',
                        'rewrite': '/tfjobs/',
                        'service': f'{hookenv.service_name()}:{port}',
                        'timeout_ms': 30000,
                    },
                ]),
            },
        },
        'containers': [
            {
                'name': 'tf-job-dashboard',
                'imageDetails': {
                    'imagePath': image_info.registry_path,
                    'username': image_info.username,
                    'password': image_info.password,
                },
                'command': [
                    '/opt/tensorflow_k8s/dashboard/backend',
                ],
                'ports': [
                    {
                        'name': 'tf-dashboard',
                        'containerPort': port,
                    },
                ],
            },
        ],
    })

    layer.status.maintenance('creating container')
    set_flag('charm.kubeflow-tf-job-dashboard.started')
