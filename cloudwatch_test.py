import boto3
from datetime import datetime, timedelta
from operator import itemgetter

ec2 = boto3.resource('ec2')

instances = ec2.instances.all()

id = 'i-0e72e9ce901394651'
instance = ec2.Instance(id)

client = boto3.client('cloudwatch')

metric_name = 'CPUUtilization'

namespace = 'AWS/EC2'
statistic = 'Average'  # could be Sum,Maximum,Minimum,SampleCount,Average

print("Start getting data")
cpu = client.get_metric_statistics(
    Period=1 * 60,
    StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
    EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
    MetricName=metric_name,
    Namespace=namespace,  # Unit='Percent',
    Statistics=[statistic],
    Dimensions=[{'Name': 'InstanceId', 'Value': id}]
)

print("=====================================")
print(cpu)
print("=====================================")

cpu_stats = []

for point in cpu['Datapoints']:
    hour = point['Timestamp'].hour
    minute = point['Timestamp'].minute
    time = hour + minute / 60
    cpu_stats.append([time, point['Average']])

cpu_stats = sorted(cpu_stats, key=itemgetter(0))

print("=====================================")
for sta in cpu_stats:
    print(sta)
print("=====================================")
