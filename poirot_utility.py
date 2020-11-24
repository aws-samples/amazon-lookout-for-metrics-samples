import sys
import time
import json
import requests

import boto3

# -----

def wait_anomaly_detector( poirot_client, arn ):
    
    prev_status = None
    while True:

        response = poirot_client.describe_anomaly_detector( AnomalyDetectorArn = arn )
        status = response["Status"]

        if status != prev_status:
            if prev_status:
                sys.stdout.write("\n")
            sys.stdout.write( status + " " )
            sys.stdout.flush()
            prev_status = status

        if status in ( "PENDING", "CREATING" ):
            sys.stdout.write(".")
            sys.stdout.flush()
            time.sleep(5)
            continue

        break

    return response


def wait_delete_anomaly_detector( poirot_client, arn ):
    
    prev_status = None
    while True:
    
        # FIXME : should catch "NotExist" exception and exit the loop

        response = poirot_client.describe_anomaly_detector( AnomalyDetectorArn = arn )
        status = response["Status"]

        if status != prev_status:
            if prev_status:
                sys.stdout.write("\n")
            sys.stdout.write( status + " " )
            sys.stdout.flush()
            prev_status = status

        if status in ( "DELETING" ):
            sys.stdout.write(".")
            sys.stdout.flush()
            time.sleep(5)
            continue

        break

    return response

# -----

def upload_to_s3( bucket_name, key, src ):
    boto3.Session().resource('s3').Bucket(bucket_name).Object(key).upload_file(src)
    return "s3://%s/%s" % ( bucket_name, key )

# -----

def get_or_create_iam_role( role_name ):

    iam = boto3.client("iam")

    assume_role_policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "poirot.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            },

            # FIXME : for alpha
            {
                "Effect": "Allow",
                "Principal": {
                    "AWS": "arn:aws:iam::036918044585:root"
                },
                "Action": "sts:AssumeRole",
                "Condition": {}
            }
        ]
    }

    try:
        create_role_response = iam.create_role(
            RoleName = role_name,
            AssumeRolePolicyDocument = json.dumps(assume_role_policy_document)
        )
        role_arn = create_role_response["Role"]["Arn"]
        print("Created %s" % role_name)

    except iam.exceptions.EntityAlreadyExistsException:
        print("Role %s already existed" % role_name )
        role_arn = boto3.resource('iam').Role(role_name).arn

    print("Attaching policies")

    iam.attach_role_policy(
        RoleName=role_name,
        PolicyArn='arn:aws:iam::aws:policy/AmazonS3FullAccess',
    )

    iam.attach_role_policy(
        RoleName = role_name,
        PolicyArn = "arn:aws:iam::aws:policy/AmazonSNSFullAccess"
    )

    print("Waiting for a minute to allow IAM role policy attachment to propagate")
    time.sleep(60)

    print(role_arn)
    
    return role_arn


def delete_iam_role( role_name ):
    iam = boto3.client("iam")
    iam.detach_role_policy( PolicyArn = "arn:aws:iam::aws:policy/AmazonS3FullAccess", RoleName = role_name )
    iam.detach_role_policy( PolicyArn = "arn:aws:iam::aws:policy/AmazonSNSFullAccess", RoleName = role_name )
    iam.delete_role(RoleName=role_name)
    print("Deleted %s" % role_name)

# -----

def get_account_id():
    sts = boto3.client("sts")
    identity = sts.get_caller_identity()
    return identity['Account']

# -----

def send_slack_message( text ):
    print( "sending message:", text )
    slack_webhook_url = "https://hooks.slack.com/services/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"
    requests.post( slack_webhook_url, json={ "text" : text } )

