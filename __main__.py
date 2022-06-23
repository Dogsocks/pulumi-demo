import pulumi
import pulumi_docker as docker

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