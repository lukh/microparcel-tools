template = """\
#ifndef {{ protocol.name.upper() }}_{{ sender.upper() }}_ROUTER_H
#define {{ protocol.name.upper() }}_{{ sender.upper() }}_ROUTER_H

#include "{{ protocol.name }}Msg.h"

class {{ protocol.name }}{{ sender }}Router {
    public:
        {% for leaf in protocol.root_node.leafs(sender) %}
        {{ protocol.name }}Msg make{{ leaf.name }}(\
{# METHOD ARGS#}
{%- for fp in leaf.fields -%}\
{%- if fp.enum -%} {{ protocol.name }}Msg::{%- endif -%}{{ fp.field_type }} in_{{ fp.name|lower }}\
{% if not loop.last %}, {% endif %}{%- endfor -%}){
\
            {{ protocol.name }}Msg msg = {{ protocol.name }}Msg();

            {% for pleaf in leaf.parents() %}
            {# UGLY, SHOULD USE ENUM... #}
            msg.set{{ pleaf.parent.name }}({{ protocol.name }}Msg::{{ pleaf.parent.name }}_{{pleaf.name}}); 
            {% endfor %}

            {% for fp in leaf.fields %}
            msg.set{{ fp.name }}(in_{{ fp.name|lower }});
            {% endfor %}
        }

        {% endfor %}

};


#endif // {{ protocol.name.upper() }}_{{ sender.upper() }}_ROUTER_H

"""