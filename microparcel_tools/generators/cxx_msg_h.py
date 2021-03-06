template = """\

#ifndef {{ protocol.name.upper() }}_MSG_H
#define  {{ protocol.name.upper() }}_MSG_H

#include "microparcel/microparcel.h"

class {{ protocol.name }}Msg: public microparcel::Message<{{ protocol.bytesize}}> {
    public:
        // --- Protocol Version ---
        static const uint8_t kProtocolVersionMajor = {{ protocol.version.major }};
        static const uint8_t kProtocolVersionMinor = {{ protocol.version.minor }};

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
        void set{{ cf.name }}({{ cf.field_type }} in_{{cf.name.lower() }}) { set<{{ cf.field_bytetype }}, {{cf.offset}}, {{cf.bitsize}}>(in_{{cf.name.lower() }}); }

        {% endfor %}


        // --- Message fields ---
        {% for f in protocol.fields %}
        // {{ f.name }}
        // {{ f.text_0(protocol.bytesize) }}
        // {{ f.text_1(protocol.bytesize) }}
        // {{ f.text_2(protocol.bytesize) }}
        {% if f.enum and not f.enum.common %}
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

#endif // {{ protocol.name.upper() }}_MSG_H


"""