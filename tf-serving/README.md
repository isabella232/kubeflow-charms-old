TensorFlow Serving for Kubeflow
===============================

This charm deploys TensorFlow Serving configured for use with
Kubeflow to Kubernetes models in Juju.


Usage
-----

Deploy an instance of this charm for each model you wish to serve, providing
the path to the trained model via the `model` config option.  It is also
useful to name the deployed application after the model.  For example, to
deploy the demo `inception` model, you would use:

```
juju deploy cs:~johnsca/kubeflow-tf-serving inception --config model=gs://kubeflow-models/inception
```

Note that, while the Google Storage URL for the demo model is publicly
accessible, it still requires Google credentials to access.  If you used
[`conjure-up canonical-kubernetes`][cdk] and deployed to [GCP][], this will
be setup automatically for you.

If you are using Kubernetes on a different provider, you can also attach
the model as a resource:

```
juju deploy cs:~johnsca/kubeflow-tf-serving inception --resource model=/path/to/model
```


[cdk]: https://kubernetes.io/docs/getting-started-guides/ubuntu/installation/#conjure-up
[GCP]: https://cloud.google.com/
