from charms.reactive import set_flag, clear_flag
from charms.reactive import when, when_not

from charms import layer


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

    layer.caas_base.pod_spec_set({
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
                        'containerPort': 8080,
                    },
                ],
            },
        ],
    })

    layer.status.maintenance('creating container')
    set_flag('charm.kubeflow-tf-job-dashboard.started')
