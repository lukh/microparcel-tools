

import os
from jinja2 import Template

from . import cxx_msg_h
from . import py_msg_py

def make_message_cxx(protocol, output_dir):
    template = Template(cxx_msg_h.template, trim_blocks=True, lstrip_blocks=True)
    
    file_content = template.render(protocol=protocol)

    output_filename = os.path.join(output_dir, protocol.name + "Msg.h")
    with open(output_filename, 'w') as fd:
        fd.write(file_content)


def make_message_py(protocol, output_dir):
    template = Template(py_msg_py.template, trim_blocks=True, lstrip_blocks=True)
    
    file_content = template.render(protocol=protocol)

    output_filename = os.path.join(output_dir, protocol.name + "Msg.py")
    with open(output_filename, 'w') as fd:
        fd.write(file_content)
