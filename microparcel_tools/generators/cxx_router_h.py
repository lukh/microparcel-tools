template = """\
#ifndef {{ protocol.name.upper() }}_{{ sender.upper() }}_ROUTER_H
#define {{ protocol.name.upper() }}_{{ sender.upper() }}_ROUTER_H

#include "{{ protocol.name }}Msg.h"

class {{ protocol.name }}{{ sender }}Router {
    public:
        {% for leaf in protocol.root_node.leafs(sender) %}
{# ##############WITHOUT SUBCAT #}
{% if not leaf.subcat %}
        static {{ protocol.name }}Msg make{{ leaf.name }}(\
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

            return msg;
        }
{# ##############WITH SUBCAT #}
        {% else %}
        {% for subcat in leaf.subcat.enum.enumerators %}
        static {{ protocol.name }}Msg make{{ leaf.name }}{{subcat}}(\
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

            {# UGLY, SHOULD USE ENUM... #}
            msg.set{{ leaf.name}}({{ protocol.name }}Msg::{{ leaf.name}}_{{ subcat }});

            {% for fp in leaf.fields %}
            msg.set{{ fp.name }}(in_{{ fp.name|lower }});
            {% endfor %}

            return msg;
        }

        {% endfor %}

        {% endif %} 

        {% endfor %}

};


#endif // {{ protocol.name.upper() }}_{{ sender.upper() }}_ROUTER_H

"""