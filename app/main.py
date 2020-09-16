import os
import requests
import schedule
import sys
import time

from kubernetes import client, config

env_namespace = os.environ.get('NAMESPACE')
env_deployment_name = os.environ.get('DEPLOYMENT_NAME')
env_deployment_labels = os.environ.get('DEPLOYMENT_LABELS')
env_min_replicas = 1
if os.environ.get('MIN_REPLICAS'):
    try:
        env_min_replicas = int(os.environ.get('MIN_REPLICAS'))
        if env_min_replicas <= 0:
            sys.exit('MIN_REPLICAS ({}) must be greater than 0'.format(env_min_replicas))
    except ValueError:
        sys.exit('MIN_REPLICAS ("{}") must be an integer value greater than 0'.format(os.environ.get('MIN_REPLICAS')))

env_max_replicas = 2
if os.environ.get('MAX_REPLICAS'):
    try:
        env_max_replicas = int(os.environ.get('MAX_REPLICAS'))
        if env_max_replicas <= 1:
            sys.exit('MAX_REPLICAS ({}) must be greater than 1'.format(env_max_replicas))
        if env_max_replicas <= env_min_replicas:
            sys.exit('MAX_REPLICAS ({}) must be greater than MIN_REPLICAS ({})'.format(env_max_replicas, env_min_replicas))
    except ValueError:
        sys.exit('MAX_REPLICAS ("{}") must be an integer value greater than 1'.format(os.environ.get('MAX_REPLICAS')))

def job():
    config.load_incluster_config()

    load = []
    coreV1 = client.CoreV1Api()
    print('Listing pods with their "loads":"')
    resp = coreV1.list_namespaced_pod(namespace=env_namespace, label_selector=env_deployment_labels, watch=False)
    for i in resp.items:
        r = requests.get('http://{}:5000/load'.format(i.status.pod_ip))
        if r.status_code == 200:
            l = r.json()['load']
            load.append(l)
            print('{}\t{}'.format(i.metadata.name, l))
        else:
            print('{}\tResponse code {}'.format(i.metadata.name, r.status_code))

    if len(load) >= 1:
        up = False
        down = True
        for i in load:
            if i == 'high':
                # try to scale up if any Pods report "high"
                # if the load on a Pod is small Kubernetes Services don't lb
                up = True
                down = False
            elif i == 'ok':
                # only scale down if all Pods report "low"
                down = False

        print('Scale up: {}; scale down: {}'.format(up, down))

        scale = 0
        if up:
            scale = 1
        elif down:
            scale = -1

        if scale == 0:
            print('No change')
        else:
            appsV1 = client.AppsV1Api()
            resp = appsV1.read_namespaced_deployment_scale(namespace="particles-test", name='particles-v1.0.0')
            current_scale = resp.to_dict()['spec']['replicas']
            print("Current scale: {}" .format(current_scale))
            desired_scale = scale + current_scale
            print("Desired scale: {}" .format(desired_scale))

            if desired_scale >= env_min_replicas and desired_scale <= env_max_replicas:
                print("Scaling from {} to {} replicas" .format(current_scale, desired_scale))
                patch = {"spec": {"replicas": desired_scale}}
                resp =appsV1.patch_namespaced_deployment_scale(namespace="particles-test", name='particles-v1.0.0', body=patch)
                print("Response: {}" .format(resp.to_dict()['spec']))
            elif desired_scale < env_min_replicas:
                print("No change: min replicas is {}" .format(env_min_replicas))
            elif desired_scale > env_max_replicas:
                print("No change: max replicas is {}" .format(env_max_replicas))

def main():
    print('Namespace:\t{}'.format(env_namespace))
    print('Deployment:\t{}\t{}'.format(env_deployment_name, env_deployment_labels))
    print('Min Replicas:\t{}'.format(env_min_replicas))
    print('Max Replicas:\t{}'.format(env_max_replicas))

    print("Scheduling job")
    schedule.every(1).minutes.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()
