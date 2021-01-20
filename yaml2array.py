#!/usr/bin/env python

import yaml

with open('./config.yaml') as f:
    y = yaml.safe_load(f)

for section in y:
    if section != 'default':
        print(section)
