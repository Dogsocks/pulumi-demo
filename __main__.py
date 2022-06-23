import pulumi
import pulumi_aws as aws
import pulumi_awsx as awsx

repo = awsx.ecr.Repository("my-repo")

image = awsx.ecr.Image("image",
                       repository_url=repo.url,
                       path="./src/web")


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