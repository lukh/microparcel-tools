template = """\
from {{ protocol.name }}Msg import {{ protocol.name }}Msg

class {{ protocol.name }}{{ sender }}Router(object):
        {% for leaf in protocol.root_node.leafs(sender) %}
        # {{ leaf.text_0(protocol.bytesize)}}
        # {{ leaf.text_1(protocol.bytesize)}}
        # {{ leaf.text_2(protocol.bytesize, protocol.common_fields)}}
{# ##############WITHOUT SUBCAT #}
{% if not leaf.subcat %}
        @staticmethod
        def make{{ leaf.name }}(\
{# METHOD COMMON ARGS#}
{%- for cf in protocol.common_fields -%}\
in_{{ cf.name|lower }}, \
{% endfor %}
{# METHOD ARGS#}
{%- for fp in leaf.fields -%}\
in_{{ fp.name|lower }}\
{% if not loop.last %}, {% endif %}{%- endfor -%}):
\
            msg = {{ protocol.name }}Msg()

            {# METHOD COMMON ARGS#}
            {% for cf in protocol.common_fields %}
            msg.set{{ cf.name }}(in_{{ cf.name|lower }})
            {% endfor %}

            {% for pleaf in leaf.parents() %}
            {# UGLY, SHOULD USE ENUM... #}
            msg.set{{ pleaf.parent.name }}({{ protocol.name }}Msg.{{ pleaf.parent.name }}.{{ pleaf.parent.name }}_{{pleaf.name}})
            {% endfor %}

            {% for fp in leaf.fields %}
            msg.set{{ fp.name }}(in_{{ fp.name|lower }})
            {% endfor %}

            return msg
{# ##############WITH SUBCAT #}
        {% else %}
        {% for subcat in leaf.subcat.enum.enumerators %}
        # {{ leaf.text_0(protocol.bytesize)}}
        # {{ leaf.text_1(protocol.bytesize)}}
        # {{ leaf.text_2(protocol.bytesize, protocol.common_fields)}}
        @staticmethod
        def make{{ leaf.name }}{{subcat}}(\
{# METHOD COMMON ARGS#}
{%- for cf in protocol.common_fields -%}\
in_{{ cf.name|lower }}, \
{% endfor %}
{# METHOD ARGS#}
{%- for fp in leaf.fields -%}\
in_{{ fp.name|lower }}\
{% if not loop.last %}, {% endif %}{%- endfor -%}):
\
            msg = {{ protocol.name }}Msg()

            {# METHOD COMMON ARGS#}
            {% for cf in protocol.common_fields %}
            msg.set{{ cf.name }}(in_{{ cf.name|lower }})
            {% endfor %}

            {% for pleaf in leaf.parents() %}
            {# UGLY, SHOULD USE ENUM... #}
            msg.set{{ pleaf.parent.name }}({{ protocol.name }}Msg.{{ pleaf.parent.name }}.{{ pleaf.parent.name }}_{{pleaf.name}})
            {% endfor %}

            {# UGLY, SHOULD USE ENUM... #}
            msg.set{{ leaf.name}}({{ protocol.name }}Msg.{{ leaf.name}}.{{ leaf.name}}_{{ subcat }})

            {% for fp in leaf.fields %}
            msg.set{{ fp.name }}(in_{{ fp.name|lower }})
            {% endfor %}

            return msg

        {% endfor %}

        {% endif %} 

        {% endfor %}


        {% for leaf in protocol.root_node.leafs(sender, True) %}
        {% if not leaf.subcat %}
        def process{{ leaf.name }}(self{% if protocol.common_fields|length > 0 or leaf.fields|length > 0 %}, {% endif %}\
{# METHOD COMMON ARGS#}
{%- for cf in protocol.common_fields -%}\
in_{{ cf.name|lower }}, \
{% endfor %}
{# METHOD ARGS#}
{%- for fp in leaf.fields -%}\
in_{{ fp.name|lower }}\
{% if not loop.last %}, {% endif %}{%- endfor -%}):
            raise NotImplementedError
        {% else %}
        {% for subcat in leaf.subcat.enum.enumerators %}
        def process{{ leaf.name }}{{ subcat }}(self{% if protocol.common_fields|length > 0 or leaf.fields|length > 0 %}, {% endif %}\
{# METHOD COMMON ARGS#}
{%- for cf in protocol.common_fields -%}\
in_{{ cf.name|lower }}, \
{% endfor %}
{# METHOD ARGS#}
{%- for fp in leaf.fields -%}\
in_{{ fp.name|lower }}\
{% if not loop.last %}, {% endif %}{%- endfor -%}):
            raise NotImplementedError

        {% endfor %}
        {% endif %}

        {% endfor %}



        def process(self, in_msg):
{% macro walk(node, level) %}
\
{# ################# NOT LEAF #}
{% if node.children and node.need_process(sender) %}
\
{% for c in node.children %}
{{ level * "    " }}    \
{%if loop.first %}
if \
{% else %}
elif \
{%endif%}
in_msg.get{{ node.name }}() == {{ protocol.name }}Msg.{{ node.name }}.{{ node.name }}_{{ c.name }}:
{% if not c.need_process(sender) %}{{ level * "    " }}        pass{% endif %}
{{ walk(c, level + 1) }}

{% endfor %}
\
{# ################# LEAF #}
{% elif node.fields_not_none and node.need_process(sender) %}
{# ### NOT SUB CAT #}
{% if not node.subcat %}
{{ level * "    " + "    " }}self.process{{ node.name }}(\
\
{# METHOD COMMON ARGS#}
{%- for cf in protocol.common_fields -%}\
in_msg.get{{ cf.name }}(), \
{% endfor %}
{% for f in node.fields %}
in_msg.get{{ f.name }}(){% if not loop.last %}, {% endif %}\
{% endfor %}
\
)
{# ### SUB CAT #}
{%else%}
{% for sc in node.subcat.enum.enumerators %}
{{ level * "    " + "    " }}\
{%if loop.first %}
if \
{%else%}
elif \
{%endif%}
in_msg.get{{ node.subcat.name}}() == {{protocol.name}}Msg.{{node.subcat.name}}.{{node.subcat.name}}_{{ sc }}:
{{ level * "    " + "        " }}self.process{{ node.name }}{{sc}}(\
\
{# METHOD COMMON ARGS#}
{%- for cf in protocol.common_fields -%}\
in_msg.get{{ cf.name }}(), \
{% endfor %}
{% for f in node.fields %}
in_msg.get{{ f.name }}(){% if not loop.last %}, {% endif %}\
{% endfor %}
\
)
{% endfor %}
{% endif %}
{% endif %}
{# ################# END LEAF #}
\
{% endmacro %}
{{ walk(protocol.root_node, 2) }}

"""