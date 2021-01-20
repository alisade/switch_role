#!/usr/bin/env python3
import argparse
import backoff
import boto3
import configparser
import uuid
from botocore import exceptions
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("role", help="role to assume")

parser.add_argument("--profile", "-p",
                    help="specify source profile to use with assume-role api call",
                    type=str)

parser.add_argument("--save", "-s",
                    help="save credentials from assume-role api call in ~/.aws/credentials",
                    action="store_true")

args = parser.parse_args()

try:
  profile = args.profile
  session = boto3.Session(profile_name=profile)
  sts = session.client('sts')
  iam = session.client('iam')
except:
  sts = boto3.client('sts')
  iam = boto3.client('iam')

try:
  sts_identity = sts.get_caller_identity()['Arn']
except exceptions.ClientError as err:
  if err.response['Error']['Code'] == 'ExpiredToken':
    print('You need to re-authenticate with Okta and try again')
    exit(1)

role = iam.get_role(RoleName=args.role)


def fatal_code(e):
  return e.response['Error']['Code'] != 'AccessDenied'


@backoff.on_exception(backoff.expo, sts.exceptions.ClientError,
                      giveup=fatal_code)
def assume_role(sts, role):
  print('Waiting for the role to become available to assume...')
  return sts.assume_role(RoleArn=role['Role']['Arn'],
                         RoleSessionName=str(uuid.uuid4()))


response = assume_role(sts, role)

creds = {
  'AWS_ACCESS_KEY_ID': response['Credentials']['AccessKeyId'],
  'AWS_SECRET_ACCESS_KEY': response['Credentials']['SecretAccessKey'],
  'AWS_SESSION_TOKEN': response['Credentials']['SessionToken']
}


def aws_creds():
  print('Run your docker command as below:')
  print('=================================')
  cmd = 'docker run -e AWS_DEFAULT_REGION=us-east-1'
  for k, v in creds.items():
    cmd = cmd + ' -e {}="{}"'.format(k, v)
  print(cmd)


def write_creds_file():
  if args.save == True:
    home = str(Path.home())
    creds_file = home + '/.aws/credentials'
    config = configparser.ConfigParser()
    config.read(creds_file)
    config['temp-aws-creds'] = creds
    with open(creds_file, 'w') as configfile:
      config.write(configfile)


if __name__ == '__main__':
  aws_creds()
  write_creds_file()
