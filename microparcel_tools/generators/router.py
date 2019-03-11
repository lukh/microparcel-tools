

import os
from jinja2 import Template

import cxx_router_h
import py_router_py

def make_router_cxx(protocol, router, output_dir):
    template = Template(cxx_router_h.template, trim_blocks=True, lstrip_blocks=True)
    
    file_content = template.render(protocol=protocol, sender=router)

    output_filename = os.path.join(output_dir, protocol.name + router + "Router.h")
    with open(output_filename, 'w') as fd:
        fd.write(file_content)

def make_router_py(protocol, router, output_dir):
    template = Template(py_router_py.template, trim_blocks=True, lstrip_blocks=True)
    
    file_content = template.render(protocol=protocol, sender=router)

    output_filename = os.path.join(output_dir, protocol.name + router + "Router.py")
    with open(output_filename, 'w') as fd:
        fd.write(file_content)



