import boto3
import os
import time

MAX_INSTANCES=1

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


def get_ec2_instances(guild_id, game):
    instances = ec2.instances.filter(
        Filters=[
            {'Name': 'tag:game', 'Values': [game]},
            {'Name': 'tag:guild_id', 'Values': [str(guild_id)]},
            {'Name': 'instance-state-name', 'Values': ['running', 'stopping','stopped']}
        ]
    )

    num = 0
    for instance in instances:
        print(f'exists: {instance.id}')
        num += 1
    return instances, num


def create_ec2(guild_id, game, hostname):
    instances = ec2.create_instances(
        ImageId='ami-00dfe2c7ce89a450b', 
        InstanceType='t3.medium',
        MinCount=1, 
        MaxCount=1,
        SecurityGroups=['valheim-sg'],
        KeyName='vh-keypair',
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {'Key': 'Name', 'Value': hostname},
                    {'Key': 'game', 'Value': game},
                    {'Key': 'guild_id', 'Value': str(guild_id)},
                    {'Key': 'hostname', 'Value': hostname},
                ]
            }
        ]
    )
    print (f'created: {instances}')
    for instance in instances:
        instance.wait_until_running()
    return instances

def create_game(guild_id, game, name):
    
    hostname = name[:10] if  len(name) > 10 else name
    hostname = f"{name.lower()}.{game.lower()}.flippn.net"

    instances, num = get_ec2_instances(guild_id, game)

    if num < MAX_INSTANCES:
        return create_ec2(guild_id, game, hostname)
    
    return None
    

def start_ec2(guild_id, game):
    instances, num = get_ec2_instances(guild_id, game)
    print(f'starting: {[instance.id for instance in instances]}')
    instances.start()
    for instance in instances:
        instance.wait_until_running()

def stop_ec2(guild_id, game):
    instances, num = get_ec2_instances(guild_id, game)
    print(f'stopping: {[instance.id for instance in instances]}')
    instances.stop()
    for instance in instances:
        instance.wait_until_stopped()

def restart_ec2(guild_id, game):
    stop_ec2(guild_id, game)
    start_ec2(guild_id, game)

def status_ec2(guild_id, game):
    instances, num = get_ec2_instances(guild_id, game)

    return_strs = []
    for instance in instances:
        server = get_r53_dns_name(instance.public_ip_address)
        fstr = f'{instance.id} \nSERVER: {server} \nIP: {instance.public_ip_address} \nSTATUS: {instance.state["Name"]}'
        print(fstr)
        return_strs.append(fstr)


def get_r53_dns_name(ip_addr):
    records = list_r53_a_records()
    if ip_addr and records:
        for record in records['ResourceRecordSets']:
            for res in record['ResourceRecords']:
                if ip_addr == res['Value']:
                    #print (f'Server: {record["Name"]}')
                    return record['Name'][:-1]

    return None

def list_r53_a_records():
    records = r53.list_resource_record_sets(
        HostedZoneId=os.getenv('AWS_HOSTED_ZONE_ID'),
    )

    return records
