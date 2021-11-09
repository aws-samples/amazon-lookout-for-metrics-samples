#!/bin/bash
sudo service docker start
sudo usermod -a -G docker ec2-user
docker ps
pip install aws-sam-cli
sam --version
sam deploy --template-file template.yaml --stack-name id-l4m-ml-ops --capabilities CAPABILITY_IAM --s3-bucket $1
bucket=$(aws cloudformation describe-stacks --stack-name id-l4m-ml-ops --query "Stacks[0].Outputs[?OutputKey=='InputBucketName'].OutputValue" --output text)
l4mrole=$(aws cloudformation describe-stacks --stack-name id-l4m-ml-ops --query "Stacks[0].Outputs[?OutputKey=='LookoutForMetricsRole'].OutputValue" --output text)
alert_lambda_name=$(aws cloudformation describe-stacks --stack-name id-l4m-ml-ops --query "Stacks[0].Outputs[?OutputKey=='AnomalyAlertFunctionName'].OutputValue" --output text)
echo "Copying Dataset"
cd datasets
unzip ecommerce.zip
aws s3 sync ecommerce/ s3://$bucket/ecommerce/ --quiet

# Go back up a directory
cd ..

# Build params.json
python ./params_builder.py $l4mrole $bucket $alert_lambda_name

# Ship params.json to bucket
aws s3 cp params.json s3://$bucket/ --quiet
