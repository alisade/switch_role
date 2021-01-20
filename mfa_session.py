#!/usr/local/opt/python@3.9/bin/python3.9
import argparse
import backoff
import boto3
import configparser
import uuid
from botocore import exceptions
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("token", help="mfa token")

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
  print('bad api key/secert')
  exit(1)

def fatal_code(e):
  return e.response['Error']['Code'] != 'AccessDenied'


@backoff.on_exception(backoff.expo, sts.exceptions.ClientError,
                      giveup=fatal_code)
def session_token(sts, serial, token):
  return sts.get_session_token(DurationSeconds=129600,
    SerialNumber=serial, TokenCode=token)

serial = sts_identity.replace('user','mfa')
response = session_token(sts, serial, args.token)

creds = {
  'AWS_ACCESS_KEY_ID': response['Credentials']['AccessKeyId'],
  'AWS_SECRET_ACCESS_KEY': response['Credentials']['SecretAccessKey'],
  'AWS_SESSION_TOKEN': response['Credentials']['SessionToken']
}


def aws_creds():
  cmd = ""
  for k, v in creds.items():
    cmd = cmd + f'{k}="{v}"\n'
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
