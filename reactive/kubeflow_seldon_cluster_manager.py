import os
from pathlib import Path

from jinja2 import Template

from charmhelpers.core import hookenv
from charms.reactive import set_flag, clear_flag, endpoint_from_flag
from charms.reactive import when, when_not

from charms import layer


@when('charm.kubeflow-seldon-cluster-manager.started')
def charm_ready():
    layer.status.active('')


@when('config.changed')
def update_model():
    clear_flag('charm.kubeflow-seldon-cluster-manager.started')


@when('layer.docker-resource.cluster-manager-image.changed')
def update_image():
    clear_flag('charm.kubeflow-seldon-cluster-manager.started')


@when_not('endpoint.redis.available')
def blocked():
    goal_state = hookenv.goal_state()
    if 'redis' in goal_state['relations']:
        layer.status.waiting('waiting for redis')
    else:
        layer.status.blocked('missing relation to redis')
    clear_flag('charm.kubeflow-seldon-cluster-manager.started')


@when('layer.docker-resource.cluster-manager-image.available')
@when('endpoint.redis.available')
@when_not('charm.kubeflow-seldon-cluster-manager.started')
def start_charm():
    layer.status.maintenance('configuring container')

    config = hookenv.config()
    image_info = layer.docker_resource.get_info('cluster-manager-image')
    redis = endpoint_from_flag('endpoint.redis.available')
    redis_application_name = redis.all_joined_units[0].application_name
    model = os.environ['JUJU_MODEL_NAME']
    rendered_podspec = Template(Path('reactive/podspec.yaml.j2').read_text()).render(
        model=model,
        config=config,
        image_info=image_info,
        redis_application_name=redis_application_name,
    )
    layer.caas_base.pod_spec_set(rendered_podspec)

    layer.status.maintenance('creating container')
    set_flag('charm.kubeflow-seldon-cluster-manager.started')
