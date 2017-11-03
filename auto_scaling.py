import boto3
import math
import random
import sys

from datetime import datetime, timedelta
from operator import itemgetter


# Start a new EC2 instance
def ec2_create(script):
    print("Start creating a new EC2 instance.")
    ec2 = boto3.resource('ec2')
    instance = ec2.create_instances(
        ImageId='ami-2d298c57',
        InstanceType='t2.micro',
        KeyName='yuanyi',
        MinCount=1,
        MaxCount=1,
        Monitoring = {
            'Enabled' : True
        },
        UserData=script,
        SecurityGroupIds=['sg-40790732'],
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'A2-userUI'
                    },
                ]
            }
        ]
    )

    print("Finish creating a new EC2 instance.")

# Terminate a EC2 instance
def ec2_destroy(id):
    print("Start destroying a new EC2 instance.")

    # create connection to ec2
    ec2 = boto3.resource('ec2')

    ec2.instances.filter(InstanceIds=[id]).terminate()

    print("Finish destroying a new EC2 instance.")


def auto_scaling(PERIOD, MAXIMUM_CPU_USAGE, MINIMUM_CPU_USAGE, SCALE_UP_RATIO, SCALE_DOWN_RATIO):
    with open('/home/ubuntu/managerUI/ec2_boot.sh', 'r') as e:
    # with open('ec2_boot.sh', 'r') as e:
        script = e.read()

    ec2 = boto3.resource('ec2')

    instances = ec2.instances.filter(Filters=[{'Name': 'tag:Name', 'Values': ['A2-userUI']}, {'Name': 'instance-state-name', 'Values': ['running']}])

    print(sum(1 for i in instances))

    for instance in instances:
        print(instance.id, instance.instance_type)

    client = boto3.client('cloudwatch')

    metric_name = 'CPUUtilization'
    namespace = 'AWS/EC2'
    statistic = 'Average'  # could be Sum,Maximum,Minimum,SampleCount,Average


    print("Start getting data")

    cpu_usage = []

    for instance in instances:

        cpu = client.get_metric_statistics(
            Period = 60, # 1 minute
            # StartTime=datetime.utcnow() - timedelta(seconds=20 * 60), # Three data points in 15 minutes
            StartTime=datetime.utcnow() - timedelta(seconds=PERIOD * 60), # One data points in 5 minutes
            EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
            MetricName=metric_name,
            Namespace=namespace,  # Unit='Percent',
            Statistics=[statistic],
            Dimensions=[{'Name': 'InstanceId', 'Value': instance.id}]
        )

        cpu_stats = []

        for point in cpu['Datapoints']:
            hour = point['Timestamp'].hour
            minute = point['Timestamp'].minute
            time = hour + minute / 60
            cpu_stats.append([time, point['Average']])

        cpu_stats = sorted(cpu_stats, key=itemgetter(0))

        data = [item[1] for item in cpu_stats]

        if(len(data) != 0):
            cpu_usage.append(sum(data)/len(data))

        print(cpu_stats)

    print("=============CPU usage for all instances==================")
    print(cpu_usage)

    if(len(cpu_usage) != 0):
        # Calculate the average cpu usage
        average_cpu_usage = sum(cpu_usage)/len(cpu_usage)
        num_of_instances = sum(1 for i in instances)
        print("Currently we have " + str(num_of_instances) + " userUI instnaces")
        print("The average CPU usage is " + str(average_cpu_usage))


        # Auto scaling
        if(average_cpu_usage > MAXIMUM_CPU_USAGE):
            print("average cpu usage is larger than " + str(MAXIMUM_CPU_USAGE))
            for i in range(0, int(num_of_instances * (SCALE_UP_RATIO-1))):
                print("Adding a new ec2 instances for userUI")
                ec2_create(script)

        elif(average_cpu_usage < MINIMUM_CPU_USAGE):
            print("average cpu usage is less than " + str(MINIMUM_CPU_USAGE))
            instances = ec2.instances.filter(Filters=[{'Name': 'tag:Name', 'Values': ['A2-userUI']}, {'Name': 'instance-state-name', 'Values': ['running']}])
            instances_id = [instance.id for instance in instances]
            random.shuffle(instances_id)

            if(num_of_instances * SCALE_DOWN_RATIO > 1):
                delete_instances_id = instances_id[:int(math.floor(num_of_instances*0.75))]
                for id in delete_instances_id:
                    print("Terminating ec2 instance : " + str(id))
                    ec2_destroy(id)

if __name__ == '__main__':

    # PERIOD = 5  # ONE MINIUTE
    # MAXIMUM_CPU_USAGE = 40  # 40% CPU USAGE
    # MINIMUM_CPU_USAGE = 10  # 10% CPU USAGE
    # SCALE_UP_RATIO = 2      # from 1 to n
    # SCALE_DOWN_RATIO = 0.75 # from 0 to 1

    args = sys.argv[1:]
    if(len(args) == 5):
        PERIOD = int(args[0])
        MAXIMUM_CPU_USAGE = float(args[1])
        MINIMUM_CPU_USAGE = float(args[2])
        SCALE_UP_RATIO = float(args[3])
        SCALE_DOWN_RATIO = float(args[4])
        auto_scaling(PERIOD, MAXIMUM_CPU_USAGE, MINIMUM_CPU_USAGE, SCALE_UP_RATIO, SCALE_DOWN_RATIO)
    else:
        print("Invalid Parameters")