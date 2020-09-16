# Demo: Particles Autoscaler

An autoscaler for the Vamp [Particles](https://github.com/magneticio/demo-particles) canary release demo.

Short demos typically don't generate enough load on the `particles-*` Pods for the Kubernetes Horizontal Pod Autoscaler to work.

To overcome this, the Particles Autoscaler periodically scapes the `/load` endpoints on the `particles-*` Pods and uses that information to autoscale the demo Deployments.

## Configuration
The autoscaler runs as a Kubernetes Job in the same Namespace as the Particles demo.

One autoscaler is required for each version of the Particles service.

### Environment Variable

The autoscaler is configured using environment variables.

#### Required
`DEPLOYMENT_NAME` - The name of the Kubernetes Deployment to be scaled.

`DEPLOYMENT_LABELS` - The Kubernetes Labels used to identify the Pods managed by the Deployment. These are the labels specified when you create the service in Vamp Cloud.

`NAMESPACE` - The Namespace to look in for the Deployment. Defaults to the Namespace in which the Job is running.

#### Optional
`MAX_REPLICAS` - The minimum number of replicas (Pods). The autoscaler will not scale below this value. Defaults to 1 replica. `MAX_REPLICAS` must be greater than 0.

`MAX_REPLICAS` - The maximum number of replicas (Pods). The autoscaler will not scale above this value. Defaults to 2 replicas. `MAX_REPLICAS` must be greater than `MAX_REPLICAS`.
