import boto3
import json

ecs = boto3.client('ecs')
# Replace with your ECS cluster name
cluster_name = 'cluster-load-testing'
def get_ecs_service_config(cluster_name, service_name):
    response = ecs.describe_services(cluster=cluster_name, services=[service_name])
    return response['services'][0]

# def update_ecs_service_desired_count(cluster_name, service_name, desired_count=0):
#     ecs = boto3.client('ecs')
#     ecs.update_service(
#         cluster=cluster_name,
#         service=service_name,
#         desiredCount=desired_count
#     )
#     print(f"Desired count for ECS service '{service_name}' in cluster '{cluster_name}' set to {desired_count}")

# def get_ecs_service_names(cluster_name, service_names):
#     response = ecs.list_services(
#         cluster=cluster_name,
#         launchType='EC2',
#         maxResults=100
#     )
#     ecs_services_arn_list = response['serviceArns']
#     for service_name in ecs_services_arn_list:
#         final_service_name = service_name.split()
#     return []

def main():
    # get this list from": https://simpl.atlassian.net/wiki/spaces/PC/pages/494993565/NYE+DB+Upgradation
    # opting out: ['ApiRunSneakerssh']
    # service_names = ['ApprovalsApiEventsProcessor', 'ApprovalsApi', 'ApprovalsApiScheduler', 'ApprovalsApiCommReqProcessor', 'Api', 'ApiRunSidekiqSchedulersh', 'Obex', 'VerificationInternal', 'VerificationServiceRunSidekiqsh']
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
    
    # service_names_list = ['obex-load-testing-Obex-jFrcVVrOeB0u']
    # service_names_list = get_ecs_service_names(cluster_name, service_names)
    service_details = {}
    # service_names_list = ['api-load-testing-Api-0BfNjkw5OxCt']  # Replace with your ECS service name
    app_sg_client = boto3.client('application-autoscaling')

    # ecs_service_config = get_ecs_service_config(cluster_name, service_names_list)


    for service_name in service_names_list:
        service_details[service_name] = {}
        ecs_service_config = get_ecs_service_config(cluster_name, service_name)
        service_details[service_name]['desiredCount'] = ecs_service_config['desiredCount']
        service_details[service_name]['deploymentConfiguration'] = ecs_service_config['deploymentConfiguration']

        #  getting scaling policy numbers and params
        try:
            asg_resource = f'service/{cluster_name}/{service_name}'
            response = app_sg_client.describe_scaling_policies(
                ServiceNamespace='ecs',
                ResourceId=asg_resource
            )
            scaling_policy_params = response['ScalingPolicies'][0]['TargetTrackingScalingPolicyConfiguration']            
            service_details[service_name]['scaling_policy_params'] = scaling_policy_params
            service_details[service_name]['PolicyName'] = response['ScalingPolicies'][0]['PolicyName']

            # getting scaling target counts
            scalable_target_response = app_sg_client.describe_scalable_targets(
                ServiceNamespace='ecs',
                ResourceIds=[asg_resource]
            )
            scalable_target_details = scalable_target_response['ScalableTargets'][0]
            service_details[service_name]['MinCapacity'] = scalable_target_details['MinCapacity']
            service_details[service_name]['MaxCapacity'] = scalable_target_details['MaxCapacity']
        except Exception as e:
            # print(f'Service: {service_name} dismissed with error: {e}. Possible: does not have scaling configured.')
            pass

    # Get current ECS service configuration
    
    # for service_config in ecs_service_config:
    #     print(service_config)
    #     service_details[service_name]['desiredCount'] = service_config['desiredCount']
    #     service_details[service_name]['deploymentConfiguration'] = service_config['deploymentConfiguration']
    #     print('printing inside 2nd for')
    #     print(service_details)
    #     # Set desired count to 0
    #     update_ecs_service_desired_count(cluster_name, service_name, 0)
    # else:
    #     print(f"ECS service '{service_name}' not found in cluster '{cluster_name}'.")
    return service_details

if __name__ == "__main__":
    service_details = main()
    with open(f"{cluster_name}-service-details.json", "w") as outfile: 
        json.dump(service_details, outfile)
    # print(service_details)

    # print(service_details)
    # bringing down service
    # 1. get all details from service -> store json
    # 2. disable autoscaling & set desired to 0

    #  bringing up to original state
    #  1. attach policy
    #  2. set desired to number saved earlier

     