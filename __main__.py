import pulumi
import pulumi_docker as docker
import pulumi_kubernetes as k8s

# Fetch the Docker Hub auth info from config.
config = pulumi.Config()
username = config.require('dockerUsername')
accessToken = config.require_secret('dockerAccessToken')

# Populate the registry info (creds and endpoint).
image_name=f'{username}/nyan-cat',
def get_registry_info(token):
    return docker.ImageRegistry(
        server='docker.io',
        username=username,
        password=token,
    )
registry_info=accessToken.apply(get_registry_info)


# Build and publish the container image.
image = docker.Image('my-image',
    build='src/web/',
    image_name=f'{username}/nyan-cat',
    registry=registry_info,
)

# Export the base and specific version image name.
pulumi.export('baseImageName', image.base_image_name)
pulumi.export('fullImageName', image.image_name)


# Create a load balanced Kubernetes service using this image, and export its IP.
app_labels = { 'app': 'myapp' }
app_dep = k8s.apps.v1.Deployment('app-dep',
    spec={
        'selector': { 'matchLabels': app_labels },
        'replicas': 3,
        'template': {
            'metadata': { 'labels': app_labels },
            'spec': {
                'containers': [{
                    'name': 'myapp',
                    'image': image.image_name,
                }],
            },
        },
    },
)
app_svc = k8s.core.v1.Service('app-svc',
    metadata={ 'labels': app_labels },
    spec={
        'type': 'LoadBalancer',
        'ports': [{ 'port': 80, 'targetPort': 80, 'protocol': 'TCP' }],
        'selector': app_labels,
    }
)
pulumi.export('appIp', app_svc.status.apply(lambda s: s.loadbalancer.ingress[0].ip))
