#!/usr/bin/python
import yaml, json, sys
sys.stdout.write(json.dumps(yaml.load(sys.stdin), sort_keys=False, indent=2))
