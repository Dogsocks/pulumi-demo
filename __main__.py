import pulumi
import pulumi_docker as docker
import pulumi_aws as aws
import pulumi_awsx as awsx


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


repo = awsx.ecr.Repository("my-repo")

image = awsx.ecr.Image("image",
                       repository_url=repo.url,
                       path="./src/web/")


cluster = aws.ecs.Cluster("default-cluster")

lb = awsx.lb.ApplicationLoadBalancer("nginx-lb")

service = awsx.ecs.FargateService("service",
                                  cluster=cluster.arn,
                                  task_definition_args=awsx.ecs.FargateServiceTaskDefinitionArgs(
                                      containers={
                                          "nginx": awsx.ecs.TaskDefinitionContainerDefinitionArgs(
                                              image=image.image_uri,
                                              memory=128,
                                              port_mappings=[awsx.ecs.TaskDefinitionPortMappingArgs(
                                                  container_port=80,
                                                  target_group=lb.default_target_group,
                                              )]
                                          )
                                      }
                                  ))

pulumi.export("url", lb.load_balancer.dns_name)