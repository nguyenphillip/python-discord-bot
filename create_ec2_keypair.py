import boto3
import os

ec2 = boto3.resource('ec2',
                     'us-east-2',
                     aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
                     aws_secret_access_key=os.getenv('AWS_SECRET_KEY'))

# create a file to store the key locally
outfile = open('vh-keypair.pem','w')

# call the boto ec2 function to create a key pair
key_pair = ec2.create_key_pair(KeyName='vh-keypair')

# capture the key and store it in a file
KeyPairOut = str(key_pair.key_material)
print(KeyPairOut)
outfile.write(KeyPairOut)