./venv/bin/gunicorn --bind 0.0.0.0:5000 --workers=1 --access-logfile access.log --error-logfile error.log app:app
aws elbv2 register-targets --target-group-arn arn:aws:elasticloadbalancing:us-east-1:611618355222:targetgroup/userUI-group/30bfb86689697b01 --targets Id=$(ec2metadata --instance-id),Port=5000
python run.py
