#!/usr/bin/env python
# Script to render F5 iRule
from jinja2 import Environment, FileSystemLoader
import yaml

# Load variable file
irule_data = yaml.load(open('./vars/addltmrulevars.yml'))

#Load Jinja2 template
env = Environment(loader = FileSystemLoader('./templates'), trim_blocks=True, lstrip_blocks=True)
template = env.get_template('irule-redirect.j2')

with open('./files/Redirect_VS-testvirtual-80.tcl', 'wb') as f:
    rule_content = template.render(irule_data)
    f.write(rule_content)
