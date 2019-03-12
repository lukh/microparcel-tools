template = """\
#ifndef {{ protocol.name.upper() }}_{{ sender.upper() }}_ROUTER_H
#define {{ protocol.name.upper() }}_{{ sender.upper() }}_ROUTER_H

#include "{{ protocol.name }}Msg.h"

class {{ protocol.name }}{{ sender }}Router {
    public:
        {% for leaf in protocol.root_node.leafs(sender) %}
        // {{ leaf.text_0(protocol.bytesize)}}
        // {{ leaf.text_1(protocol.bytesize)}}
        // {{ leaf.text_2(protocol.bytesize, protocol.common_fields)}}
{# ##############WITHOUT SUBCAT #}
{% if not leaf.subcat %}
        static {{ protocol.name }}Msg make{{ leaf.name }}(\
{# METHOD COMMON ARGS#}
{%- for cf in protocol.common_fields -%}\
{%- if cf.enum -%} {{ protocol.name }}Msg::{%- endif -%}{{ cf.field_type }} in_{{ cf.name|lower }}, \
{% endfor %}
{# METHOD ARGS#}
{%- for fp in leaf.fields -%}\
{%- if fp.enum -%} {{ protocol.name }}Msg::{%- endif -%}{{ fp.field_type }} in_{{ fp.name|lower }}\
{% if not loop.last %}, {% endif %}{%- endfor -%}){
\
            {{ protocol.name }}Msg msg = {{ protocol.name }}Msg();

            {# METHOD COMMON ARGS#}
            {% for cf in protocol.common_fields %}
            msg.set{{ cf.name }}(in_{{ cf.name|lower }});
            {% endfor %}

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
        // {{ leaf.text_0(protocol.bytesize)}}
        // {{ leaf.text_1(protocol.bytesize)}}
        // {{ leaf.text_2(protocol.bytesize, protocol.common_fields)}}
        static {{ protocol.name }}Msg make{{ leaf.name }}{{subcat}}(\
{# METHOD COMMON ARGS#}
{%- for cf in protocol.common_fields -%}\
{%- if cf.enum -%} {{ protocol.name }}Msg::{%- endif -%}{{ cf.field_type }} in_{{ cf.name|lower }}\
{% endfor %}
{# METHOD ARGS#}
{%- for fp in leaf.fields -%}\
{%- if fp.enum -%} {{ protocol.name }}Msg::{%- endif -%}{{ fp.field_type }} in_{{ fp.name|lower }}\
{% if not loop.last %}, {% endif %}{%- endfor -%}){
\
            {{ protocol.name }}Msg msg = {{ protocol.name }}Msg();

            {# METHOD COMMON ARGS#}
            {% for cf in protocol.common_fields %}
            msg.set{{ cf.name }}(in_{{ cf.name|lower }});
            {% endfor %}

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


        {% for leaf in protocol.root_node.leafs(sender, True) %}
        {% if not leaf.subcat %}
        virtual void process{{ leaf.name }}(\
{# METHOD COMMON ARGS#}
{%- for cf in protocol.common_fields -%}\
{%- if cf.enum -%} {{ protocol.name }}Msg::{%- endif -%}{{ cf.field_type }} in_{{ cf.name|lower }}, \
{% endfor %}
{# METHOD ARGS#}
{%- for fp in leaf.fields -%}\
{%- if fp.enum -%} {{ protocol.name }}Msg::{%- endif -%}{{ fp.field_type }} in_{{ fp.name|lower }}\
{% if not loop.last %}, {% endif %}{%- endfor -%}) = 0;
        {% else %}
        {% for subcat in leaf.subcat.enum.enumerators %}
        virtual void process{{ leaf.name }}{{ subcat }}({# METHOD ARGS#}
{# METHOD COMMON ARGS#}
{%- for cf in protocol.common_fields -%}\
{%- if cf.enum -%} {{ protocol.name }}Msg::{%- endif -%}{{ cf.field_type }} in_{{ cf.name|lower }}, \
{% endfor %}
{%- for fp in leaf.fields -%}\
{%- if fp.enum -%} {{ protocol.name }}Msg::{%- endif -%}{{ fp.field_type }} in_{{ fp.name|lower }}\
{% if not loop.last %}, {% endif %}{%- endfor -%}) = 0;
        {% endfor %}
        {% endif %}
        {% endfor %}



        void process({{ protocol.name }}Msg &in_msg){
{% macro walk(node, level) %}
\
{# ################# NOT LEAF #}
{% if node.children and node.need_process(sender) %}
{{ level * "    " }}    switch(in_msg.get{{ node.name }}(){
\
{% for c in node.children %}
{{ level * "    " }}        case {{ protocol.name }}Msg::{{ node.name }}_{{ c.name }}:
{{ walk(c, level + 2) }}
{{ level * "    " }}            break;

{% endfor %}
\
{{ level * "    " + "    " }}}
\
{# ################# LEAF #}
{% elif node.fields and node.need_process(sender) %}
{# ### NOT SUB CAT #}
{% if not node.subcat %}
{{ level * "    " + "    " }}process{{ node.name }}(\
\
{% for f in protocol.common_fields %}
in_msg.get{{ f.name }}(), \
{% endfor %}
{% for f in node.fields %}
in_msg.get{{ f.name }}(){% if not loop.last %}, {% endif %}\
{% endfor %}
\
);
{# ### SUB CAT #}
{%else%}
{{ level * "    " + "    " }}switch(msg.get{{ node.subcat.name}}()){
{% for sc in node.subcat.enum.enumerators %}
{{ level * "    " + "        " }}case {{protocol.name}}Msg::{{node.subcat.name}}_{{ sc }}:
{{ level * "    " + "            " }}process{{ node.name }}{{sc}}(\
\
{% for f in protocol.common_fields %}
in_msg.get{{ f.name }}(), \
{% endfor %}
{% for f in node.fields %}
in_msg.get{{ f.name }}(){% if not loop.last %}, {% endif %}\
{% endfor %}
\
);
{{ level * "    " + "            " }}break;
{% endfor %}
{{ level * "    " + "        " }}}
{% endif %}
{% endif %}
{# ################# END LEAF #}
\
{% endmacro %}
{{ walk(protocol.root_node, 2) }}
        }
};


#endif // {{ protocol.name.upper() }}_{{ sender.upper() }}_ROUTER_H

"""