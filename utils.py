import boto3
import os
import time

ec2 = boto3.resource(
    'ec2',
    region_name=os.getenv('AWS_REGION'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_KEY'))

r53 = boto3.client(
    'route53',
    region_name=os.getenv('AWS_REGION'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_KEY'))


def check_ec2_instances():
    instances = ec2.instances.filter(
        Filters=[
            {'Name': 'tag:game', 'Values': ['valheim']},
            {'Name': 'instance-state-name', 'Values': ['running', 'stopping','stopped']}
        ]
    )

    num = 0
    for instance in instances:
        print(f'exists: {instance.id}')
        num += 1
    return instances, num


def create_ec2():
    instance = ec2.create_instances(
        ImageId='ami-08962a4068733a2b6', 
        InstanceType='t3.medium',
        MinCount=1, 
        MaxCount=1,
        SecurityGroups=['valheim-sg'],
        KeyName='vh-keypair',
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'game',
                        'Value': 'valheim'
                    }
                ]
            }
        ]
    )
    print (f'created: {instance}')
    return instance


def start_ec2(instances):
    print(f'starting: {[instance.id for instance in instances]}')
    instances.start()
    for instance in instances:
        instance.wait_until_running()

def stop_ec2(instances):
    print(f'stopping: {[instance.id for instance in instances]}')
    instances.stop()
    for instance in instances:
        instance.wait_until_stopped()

def restart_ec2(instances):
    stop_ec2(instances)
    start_ec2(instances)

def status_ec2(instances, records):
    return_strs = []
    for instance in instances:
        server = get_r53_dns_name(records, instance.public_ip_address)
        fstr = f'{instance.id} \nSERVER: {server} \nIP: {instance.public_ip_address} \nSTATUS: {instance.state["Name"]}'
        print(fstr)
        return_strs.append(fstr)


def list_r53_a_records():
    records = r53.list_resource_record_sets(
        HostedZoneId=os.getenv('AWS_HOSTED_ZONE_ID'),
    )

    return records

def get_r53_dns_name(records, ip_addr):
    if ip_addr:
        for record in records['ResourceRecordSets']:
            for res in record['ResourceRecords']:
                if ip_addr == res['Value']:
                    #print (f'Server: {record["Name"]}')
                    return record['Name'][:-1]

    return None



if __name__ == "__main__":
    instances, num = check_ec2_instances()
    records = list_r53_a_records()

    if num == 0:
        instances = create_ec2()
    
    status_ec2(instances, records)
