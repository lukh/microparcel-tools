message_template = """\
#include "microparcel.h"

class {{ protocol.name }}Msg: public microparcel::Message<{{ protocol.bytesize}}> {
    // --- Common enums ---
    {% for ce in protocol.common_enums.values() %}
    // {{ ce.name }}
    enum {{ ce.name }} {
        {% for enumerator in ce.named_enumerators %}
        {{ enumerator }} = {{ loop.index - 1 }},
        {% endfor %}
    };
    {% endfor %}

    // --- Common fields ---
    {% for cf in protocol.common_fields %}
    // {{ cf.name }}
    // {{ cf.text_0(protocol.bytesize) }}
    // {{ cf.text_1(protocol.bytesize) }}
    // {{ cf.text_2(protocol.bytesize) }}
    {% if cf.enum %}
    enum {{ cf.enum.name }} {
        {% for enumerator in cf.enum.named_enumerators %}
        {{ enumerator }} = {{ loop.index - 1 }},
        {% endfor %}
    };
    {% endif %}
    {{cf.field_type}} get{{ cf.name }}() { return ({{cf.field_type}}) get<{{ cf.field_bytetype }}, {{cf.offset}}, {{cf.bitsize}}>(); }
    {% endfor %}


    // --- Message fields ---
    {% for f in protocol.fields %}
    // {{ f.name }}
    // {{ f.text_0(protocol.bytesize) }}
    // {{ f.text_1(protocol.bytesize) }}
    // {{ f.text_2(protocol.bytesize) }}
    {% if f.enum %}
    enum {{ f.enum.name }} {
        {% for enumerator in f.enum.named_enumerators %}
        {{ enumerator }} = {{ loop.index - 1 }},
        {% endfor %}
    };
    {% endif %}
    {{f.field_type}} get{{ f.name }}() { return ({{f.field_type}}) get<{{ f.field_bytetype }}, {{f.offset}}, {{f.bitsize}}>(); }
    void set{{ f.name }}({{ f.field_type }} in_{{f.name.lower() }}) { set<{{ f.field_bytetype }}, {{f.offset}}, {{f.bitsize}}>(in_{{f.name.lower() }}); }
    {% endfor %}
};

"""

import os
from jinja2 import Template


def make_message_cxx(protocol, output_dir):
    template = Template(message_template)
    
    file_content = template.render(protocol=protocol)

    output_filename = os.path.join(output_dir, protocol.name + "Msg.h")
    with open(output_filename, 'w') as fd:
        fd.write(file_content)
