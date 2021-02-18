Overview
========

This charm deploys the Ambassador API Gateway configured for use with
Kubeflow to Kubernetes models in Juju.

It exposes two different services publicly, JupyterHub and TensorFlow Job Dashboard.
They are located at `/hub/` and `/jobs/`, respectively.

Deploying
=========

This charm is available in the Charm store at [cs:~kubeflow-charmers/kubeflow-ambassador][ambassador-cs].

Alternatively, you can deploy this charm locally. To do so, first clone this repo:

    git clone https://github.com/juju-solutions/charm-kubeflow-ambassador.git
    cd charm-kubeflow-ambassador

Next, ensure that you have `charm-tools` installed, and build this charm:

    sudo snap install charm-tools
    charm build

Finally, use Juju to deploy this charm, defining which image to base this
off of:

    juju deploy ./builds/kubeflow-ambassador/ --resource ambassador-image=quay.io/datawire/ambassador:0.30.1

You can then expose the service locally with `kubectl`:

    kubectl port-forward svc/juju-kubeflow-ambassador 8081:80

You can then access Ambassador in your browser at `localhost:8081`. Some useful
endpoints:

    http://localhost:8081/tfjobs/ui/
    http://localhost:8081/hub/

[ambassador-cs]: https://jujucharms.com/u/kubeflow-charmers/kubeflow-ambassador/
