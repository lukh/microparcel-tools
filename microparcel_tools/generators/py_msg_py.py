template = """\
from enum import Enum
import microparcel as mp

class {{ protocol.name }}Msg(mp.Message):
    PROTOCOL_VERSION_MAJOR = {{ protocol.version.major }}
    PROTOCOL_VERSION_MINOR = {{ protocol.version.minor }}

    def __init__(self):
        super({{ protocol.name }}Msg, self).__init__(size={{ protocol.bytesize}})

    # --- Common enums ---
    {% for ce in protocol.common_enums.values() %}
    # {{ ce.name }}
    class {{ ce.name }}(Enum):
        {% for enumerator in ce.named_enumerators %}
        {{ enumerator }} = {{ loop.index - 1 }}
        {% endfor %}
    {% endfor %}

    # --- Common fields ---
    {% for cf in protocol.common_fields %}
    # {{ cf.name }}
    # {{ cf.text_0(protocol.bytesize) }}
    # {{ cf.text_1(protocol.bytesize) }}
    # {{ cf.text_2(protocol.bytesize) }}
    {% if cf.enum %}
    class {{ cf.enum.name }}(Enum):
        {% for enumerator in cf.enum.named_enumerators %}
        {{ enumerator }} = {{ loop.index - 1 }}
        {% endfor %}
    {% endif %}
    def get{{ cf.name }}(self):
        {% if cf.enum %}
        return {{ protocol.name }}Msg.{{cf.enum.name}}( self.get({{cf.offset}}, {{cf.bitsize}})  )
        {% else %}
        return self.get({{cf.offset}}, {{cf.bitsize}})
        {% endif %}
    def set{{ cf.name }}(self, in_{{ cf.name.lower() }}):
        {% if cf.enum %}
        self.set({{cf.offset}}, {{cf.bitsize}}, in_{{ cf.name.lower() }}.value)
        {% else %}
        self.set({{cf.offset}}, {{cf.bitsize}}, in_{{ cf.name.lower() }})
        {% endif %}

    {% endfor %}


    # --- Message fields ---
    {% for f in protocol.fields %}
    # {{ f.name }}
    # {{ f.text_0(protocol.bytesize) }}
    # {{ f.text_1(protocol.bytesize) }}
    # {{ f.text_2(protocol.bytesize) }}
    {% if f.enum %}
    class {{ f.enum.name }}(Enum):
        {% for enumerator in f.enum.named_enumerators %}
        {{ enumerator }} = {{ loop.index - 1 }}
        {% endfor %}
    {% endif %}
    def get{{ f.name }}(self):
        {% if f.enum %}
        return {{ protocol.name }}Msg.{{f.enum.name}}( self.get({{f.offset}}, {{f.bitsize}})  )
        {% else %}
        return self.get({{f.offset}}, {{f.bitsize}})
        {% endif %}
    def set{{ f.name }}(self, in_{{ f.name.lower() }}):
        {% if f.enum %}
        self.set({{f.offset}}, {{f.bitsize}}, in_{{ f.name.lower() }}.value)
        {% else %}
        self.set({{f.offset}}, {{f.bitsize}}, in_{{ f.name.lower() }})
        {% endif %}
        
    {% endfor %}

"""