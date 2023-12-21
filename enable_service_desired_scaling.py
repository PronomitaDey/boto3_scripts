import boto3
import json

ecs = boto3.client('ecs')
app_sg_client = boto3.client('application-autoscaling')
# Replace with your ECS cluster name
cluster_name = 'cluster-load-testing'

def update_desired_count(service_name, desiredCount):
    ecs.update_service(
        cluster=cluster_name,
        service=service_name,
        desiredCount=desiredCount
    )
    print(f'desired set to {desiredCount} for: {service_name}')

def enable_service_auto_scaling(service_name, my_service_details):
    response = app_sg_client.register_scalable_target(
        ServiceNamespace='ecs',
        ResourceId=f'service/{cluster_name}/{service_name}',
        ScalableDimension='ecs:service:DesiredCount',
        MinCapacity=my_service_details['MinCapacity'],
        MaxCapacity=my_service_details['MaxCapacity']
        )
    put_response = app_sg_client.put_scaling_policy(
        PolicyName = my_service_details['PolicyName'],
        ServiceNamespace='ecs',
        ResourceId=f'service/{cluster_name}/{service_name}',
        ScalableDimension='ecs:service:DesiredCount',
        PolicyType='TargetTrackingScaling',
        TargetTrackingScalingPolicyConfiguration={
            'TargetValue': my_service_details['scaling_policy_params']['TargetValue'],
            'PredefinedMetricSpecification': {
                'PredefinedMetricType': my_service_details['scaling_policy_params']['PredefinedMetricSpecification']['PredefinedMetricType'],
                'ResourceLabel': my_service_details['scaling_policy_params']['PredefinedMetricSpecification']['ResourceLabel']
            },
            'ScaleOutCooldown': my_service_details['scaling_policy_params']['ScaleOutCooldown'],
            'ScaleInCooldown': my_service_details['scaling_policy_params']['ScaleInCooldown'],
            'DisableScaleIn': my_service_details['scaling_policy_params']['DisableScaleIn']
        }
    )

def get_service_info(cluster_name):
    with open(f"{cluster_name}-service-details-test.json", "r") as infile:
        service_details = json.load(infile)
    print(type(service_details))
    return service_details

if __name__ == '__main__':
    service_names_list = [
        "api-load-testing-Api-0BfNjkw5OxCt",
        "approvals-api-load-testing-ApprovalsApiEventsProcessor-aY7pGPXFVxnr",
        "approvals-api-load-testing-ApprovalsApiCommReqProcessor-udLBnt51eyGE",
        "approvals-api-load-testing-ApprovalsApi-ln22U3PGODgT",
        "approvals-api-load-testing-ApprovalsApiScheduler-O77Abmz10jHR",
        "api-load-testing-ApiRunSidekiqSchedulersh-YcSkG6UOA6uN",
        "obex-load-testing-Obex-jFrcVVrOeB0u",
        "verification-service-load-testing-VerificationInternal-yw3RIDi7QAux",
        "verification-service-load-testing-VerificationServiceRunSidekiqsh-hU3SylcHIpig"
    ]
    service_details = get_service_info(cluster_name)

    for service_name in service_names_list:
        if 'scaling_policy_params' in service_details[service_name]:
            enable_service_auto_scaling(service_name,service_details[service_name])
        update_desired_count(service_name, service_details[service_name]['desiredCount'])
    

    