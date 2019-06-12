import os
import sys
import json
from jsoncomment import JsonComment
import cerberus
import collections


def validate_protocol_schema(protocol_schema):
    sch = {
        "name":{"type":"string", "required":True},
        "version":{"type":"dict", "required":True, 'schema': {'major':{'type': 'integer', "required":True}, 'minor':{'type': 'integer', "required":True}} },
        "endpoints":{"type":"list", "required":True, 'schema': {'type': 'string'}},
        "common_enums":
        {
            "type":"list", "required":True, 
            'schema': 
            {
                'type': 'dict',
                'schema':
                {
                    'name':{'type':'string',"required":True},
                    'enumerators':{'type':'list',"required":True, 'schema': {'type': 'string'}}
                }
            }
        },

        "common_fields":
        {
            "type":"list", "required":True, 
            'schema': 
            {
                'type': 'dict', 
                'schema':
                {
                    'name':{'type':'string',"required":True},
                    'short_name':{'type':'string',"required":True},
                    'bitsize':{'type':'integer',"required":False},
                    'enumerators':{'type':'list',"required":False, 'schema': {'type': 'string'}},
                    'enum_name':{'type':'string',"required":False}
                }
            }
        },
        "nodes":{
            "type":"dict", "required":True
        }
    }

    validator = cerberus.Validator(sch)
    if not validator.validate(protocol_schema):
        return (False, str(validator.errors))

    ########################################
    # Recursives:
    ########################################
    def rec_validation(node):
        # current node
        sch = {
            'name':{'type':'string',"required":True},
            'subcat':{'type':'list', 'required':False, 'schema':{'type':'string'}},
            'fields':{'type':'list', 'required':False, 
                'schema':{'type':'dict', 
                    'schema':{
                        'name':{'type':'string',"required":True},
                        'short_name':{'type':'string',"required":True},
                        'bitsize':{'type':'integer',"required":False},
                        'enum_name':{'type':'string',"required":False},
                        'enumerators':{'type':'list',"required":False, 'schema': {'type': 'string'}},
                        'offset':{'type':'integer', 'required':False}
                    }
                }
            },
            'senders':{'type':'list', 'required':False, 'schema':{'type':'string'}},
            'children':{'type':'list', 'required':False},
            'offset':{'type':'integer', 'required':False}
        }

        validator = cerberus.Validator(sch)
        if not validator.validate(node):
            return (False, str(validator.errors))


        if 'children' in node:
            for c in node['children']:
                (st, msg) = rec_validation(c)
                if not st:
                    return False, msg

        return (True, "")

    return rec_validation(protocol_schema['nodes'])

