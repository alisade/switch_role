#!/usr/bin/env python3
import boto3
import os
import yaml
from configparser import ConfigParser
from sys import argv
from sys import exit
from os import environ
env_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN', 'CDK_DEFAULT_ACCOUNT', 'AWS_DEFAULT_REGION', 'KUBECONFIG']

# unset current vars set, we want to use the instance role
def unset():
    for _e in env_vars:
        print('unset {}'.format(_e))

if len(argv) < 2:
    unset()
    exit()
else:
   deploy_env = argv[1]
    
def load_yaml():
    with open(os.path.dirname(argv[0]) + '/config.yaml') as f:
        config_data = yaml.safe_load(f)
    return config_data

config = load_yaml()

for _e in env_vars:
    if (os.environ.get(_e)):
        del os.environ[_e]

client = boto3.client('sts')
response = client.assume_role(RoleArn=config[deploy_env]['cross_account_role_arn'], RoleSessionName=deploy_env, ExternalId=config[deploy_env].get('externalid'))

def kubeconfig():
    print('export KUBECONFIG={}'.format(config[deploy_env]['kubeconfig']))

def aws_envs():
    # Exporting AWS Credentials
    print('export AWS_ACCESS_KEY_ID={}'.format(response['Credentials']['AccessKeyId']))
    print('export AWS_SECRET_ACCESS_KEY={}'.format(response['Credentials']['SecretAccessKey']))
    print('export AWS_SESSION_TOKEN={}'.format(response['Credentials']['SessionToken']))

def cdk_envs():
    # Exporting CDK required variables
    print('export CDK_DEFAULT_ACCOUNT={}'.format(config[deploy_env]['account_number']))
    print('export AWS_DEFAULT_REGION={}'.format(config[deploy_env]['region']))

if __name__ == '__main__':
    unset()
    aws_envs()
    cdk_envs()
    kubeconfig()
