from pathlib import Path

from charmhelpers.core import hookenv
from charmhelpers.core import unitdata

from charms.reactive import set_flag, clear_flag
from charms.reactive import when, when_not
from charms.reactive import data_changed

from charms import layer


@when('charm.kubeflow-tf-serving.has-model')
@when('charm.kubeflow-tf-serving.started')
def charm_ready():
    layer.status.active('')


@when('config.changed.model')
def update_model():
    clear_flag('charm.kubeflow-tf-serving.has-model')


@when('layer.docker-resource.tf-serving-image.changed')
def update_image():
    clear_flag('charm.kubeflow-tf-serving.started')


@when_not('charm.kubeflow-tf-serving.has-model')
def get_model():
    is_resource = True
    model = None
    # model = layer.kubeflow_tf_serving.get_model_from_resource()
    if not model:
        is_resource = False
        model = layer.kubeflow_tf_serving.get_model_from_config()
    if model:
        if data_changed('charm.kubeflow-tf-serving.model', model):
            set_flag('charm.kubeflow-tf-serving.has-model')
            clear_flag('charm.kubeflow-tf-serving.started')
            unitdata.kv().set('charm.kf-tf-serving.model', model)
            unitdata.kv().set('charm.kf-tf-serving.is-resource', is_resource)
    else:
        clear_flag('charm.kubeflow-tf-serving.has-model')
        unitdata.kv().unset('charm.kubeflow-tf-serving.model')
        layer.status.waiting('waiting for model')


@when('layer.docker-resource.tf-serving-image.available')
@when('charm.kubeflow-tf-serving.has-model')
@when_not('charm.kubeflow-tf-serving.started')
def start_charm():
    layer.status.maintenance('configuring container')

    image_info = layer.docker_resource.get_info('tf-serving-image')
    is_resource = unitdata.kv().get('charm.kf-tf-serving.is-resource')
    if is_resource:
        res_path = unitdata.kv().get('charm.kf-tf-serving.model')
        model_path = '/mnt/tf-serving/model'
        model_data = Path(res_path).read_bytes()
        files = [{
            'name': 'model',
            'mountPath': '/mnt/tf-serving/',
            'files': {
                'model': model_data.encode('utf-8'),
            },
        }]
    else:
        model_path = unitdata.kv().get('charm.kf-tf-serving.model')
        files = []

    layer.caas_base.pod_spec_set({
        'containers': [
            {
                'name': 'tf-serving',
                'imageDetails': {
                    'imagePath': image_info.registry_path,
                    'username': image_info.username,
                    'password': image_info.password,
                },
                'command': [
                    '/usr/bin/tensorflow_model_server',
                    '--port=9000',
                    '--model_name={}'.format(hookenv.service_name()),
                    '--model_base_path={}'.format(model_path),
                ],
                'ports': [
                    {
                        'name': 'tf-serving',
                        'containerPort': 9000,
                    },
                ],
                'files': files,
                # TODO?
                # 'resources': {
                #     'limits': {
                #         'cpu': '4',
                #         'memory': '4Gi',
                #     },
                #     'requests': {
                #         'cpu': '1',
                #         'memory': '1Gi',
                #     },
                # },
                # 'securityContext': {
                #     'fsGroup': 1000,
                #     'runAsUser': 1000,
                # },
            },
        ],
    })

    layer.status.maintenance('creating container')
    set_flag('charm.kubeflow-tf-serving.started')
