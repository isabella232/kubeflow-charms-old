Overview
========

[Seldon Core](https://github.com/SeldonIO/seldon-core) is an
open source platform for deploying machine learning models on Kubernetes.

This charm deploys the Cluster Manager component of Seldon, configured for
use with Kubeflow to Kubernetes models in Juju.

Usage
=====

This charm must be deployed to a Kubernetes model in Juju and related to
Redis:

```
juju deploy cs:~johnsca/kubeflow-seldon-cluster-manager
juju deploy cs:~johnsca/redis
juju add-relation kubeflow-seldon-cluster-manager redis
```

To submit models to be trained or served, you must create a `SeldonDeployment`
custom resource.  Currently, the custom resource definition for this must be
loaded manually via:

```
kubectl create -n $juju_model_name -f https://raw.githubusercontent.com/juju-solutions/charm-kubeflow-seldon-cluster-manager/start/files/crd-v1alpha1.yaml
```

The specific `SeldonDeployment` that you create will depend on how and what
image you are wanting to serve, but a simple example might look like:

```yaml
---
apiVersion: machinelearning.seldon.io/v1alpha1
kind: SeldonDeployment
metadata:
  labels:
    app: seldon
  name: mymodel
  namespace: default
spec:
  annotations:
    deployment_version: v1
    project_name: mymodel
  name: mymodel
  predictors:
  - annotations:
      predictor_version: v1
    componentSpec:
      spec:
        containers:
        - image: seldonio/mock_classifier:1.0
          imagePullPolicy: Always
          name: mymodel
          volumeMounts: []
        terminationGracePeriodSeconds: 1
        volumes: []
    graph:
      children: []
      endpoint:
        type: REST
      name: mymodel
      type: MODEL
    name: mymodel
    replicas: 1
```
