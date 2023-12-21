import json 
import boto3

app_sg_client = boto3.client('application-autoscaling')
ecs = boto3.client('ecs')
cluster_name = 'cluster-load-testing'

def disable_auto_scaling(service_name):
    response = app_sg_client.deregister_scalable_target(
        ServiceNamespace='ecs',
        ResourceId=f'service/{cluster_name}/{service_name}',
        ScalableDimension='ecs:service:DesiredCount'
    )
    print(f'auto scaling diabled for {service_name}')

def downscale_service(service_name):
    ecs.update_service(
        cluster=cluster_name,
        service=service_name,
        desiredCount=0
    )
    print(f'desired set to 0 for: {service_name}')

def get_service_info(cluster_name):
    with open(f"{cluster_name}-service-details-test.json", "r") as infile:
        service_details = json.load(infile)
    print(type(service_details))
    return service_details

if __name__ == '__main__':
    service_details = get_service_info(cluster_name)
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
    for service_name in service_names_list:
        if 'scaling_policy_params' in service_details[service_name]:
            disable_auto_scaling(service_name)
        downscale_service(service_name)