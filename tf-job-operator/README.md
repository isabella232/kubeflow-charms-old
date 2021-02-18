TensorFlow Training for Kubeflow
================================

This charm deploys the TensorFlow Training component of Kubeflow to Kubernetes
models in Juju.


Usage
=====

To submit models to be trained, you must create a `TFJob` custom resource
in Kubernetes.  For example, to submit the distributed mnist model, which is
used for e2e testing, you can use:

```
kubectl create -n $namespace \
    -f https://raw.githubusercontent.com/kubeflow/tf-operator/master/examples/v1alpha2/dist-mnist/tf_job_mnist.yaml
```

(Note: The namespace is the name of the Kubernetes model in Juju that this
charm is deployed into.)

You can then check the status of the job via either the TensorFlow Dashboard,
or kubectl:

```
kubectl get -o yaml -n $namespace tfjobs dist-mnist-for-e2e-test
```
