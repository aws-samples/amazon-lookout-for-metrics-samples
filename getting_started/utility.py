import sys
import time
import json
import pathlib

import boto3
from botocore.exceptions import ClientError

# -----

def wait_anomaly_detector( lookoutmetrics_client, arn ):
    
    prev_status = None
    while True:

        response = lookoutmetrics_client.describe_anomaly_detector( AnomalyDetectorArn = arn )
        status = response["Status"]

        if status != prev_status:
            if prev_status:
                sys.stdout.write("\n")
            sys.stdout.write( status + " " )
            sys.stdout.flush()
            prev_status = status

        if status in ( "ACTIVATING", "BACK_TEST_ACTIVATING", "BACK_TEST_ACTIVE" ):
            sys.stdout.write(".")
            sys.stdout.flush()
            time.sleep(5)
            continue

        break

    return response


def wait_delete_anomaly_detector( lookoutmetrics_client, arn ):
    
    prev_status = None
    while True:
    
        try:
            response = lookoutmetrics_client.describe_anomaly_detector( AnomalyDetectorArn = arn )
            status = response["Status"]
        except lookoutmetrics_client.exceptions.ResourceNotFoundException:
            break

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
                    "Service": "lookoutmetrics.amazonaws.com"
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
            },

            # FIXME : for beta
            {
                "Effect": "Allow",
                "Principal": {
                    "AWS": "arn:aws:iam::458402630025:root"
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

def create_bucket(bucket_name, region=None):
    """Create an S3 bucket in a specified region

    If a region is not specified, the bucket is created in the S3 default
    region (us-east-1).

    :param bucket_name: Bucket to create
    :param region: String region to create bucket in, e.g., 'us-west-2'
    :return: True if bucket created, else False
    """

    # Create bucket
    try:
        if region is None:
            s3_client = boto3.client('s3')
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client = boto3.client('s3', region_name=region)
            location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name,
                                    CreateBucketConfiguration=location)
    except ClientError as e:
        print(e)
        return False
    return True

class DisplayablePath(object):
    display_filename_prefix_middle = '├──'
    display_filename_prefix_last = '└──'
    display_parent_prefix_middle = '    '
    display_parent_prefix_last = '│   '

    def __init__(self, path, parent_path, is_last):
        self.path = pathlib.Path(str(path))
        self.parent = parent_path
        self.is_last = is_last
        if self.parent:
            self.depth = self.parent.depth + 1
        else:
            self.depth = 0

    @property
    def displayname(self):
        if self.path.is_dir():
            return self.path.name + '/'
        return self.path.name

    @classmethod
    def make_tree(cls, root, parent=None, is_last=False, criteria=None):
        root = pathlib.Path(str(root))
        criteria = criteria or cls._default_criteria

        displayable_root = cls(root, parent, is_last)
        yield displayable_root

        children = sorted(list(path
                               for path in root.iterdir()
                               if criteria(path)),
                          key=lambda s: str(s).lower())
        count = 1
        for path in children:
            is_last = count == len(children)
            if path.is_dir():
                yield from cls.make_tree(path,
                                         parent=displayable_root,
                                         is_last=is_last,
                                         criteria=criteria)
            else:
                yield cls(path, displayable_root, is_last)
            count += 1

    @classmethod
    def _default_criteria(cls, path):
        return True

    @property
    def displayname(self):
        if self.path.is_dir():
            return self.path.name + '/'
        return self.path.name

    def displayable(self):
        if self.parent is None:
            return self.displayname

        _filename_prefix = (self.display_filename_prefix_last
                            if self.is_last
                            else self.display_filename_prefix_middle)

        parts = ['{!s} {!s}'.format(_filename_prefix,
                                    self.displayname)]

        parent = self.parent
        while parent and parent.parent is not None:
            parts.append(self.display_parent_prefix_middle
                         if parent.is_last
                         else self.display_parent_prefix_last)
            parent = parent.parent

        return ''.join(reversed(parts))