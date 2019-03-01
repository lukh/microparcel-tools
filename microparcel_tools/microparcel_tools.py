# -*- coding: utf-8 -*-

from common import *
from tools import validate_protocol_schema

class Protocol(object):
    def __init__(self, source_schema):
        # schema validation
        status, msg = validate_protocol_schema(source_schema)
        if not status:
            raise ValueError(msg)

        # building the protocol
        self.name = source_schema['name']
        self.endpoints = source_schema['endpoints']
        
        # common enums and fields
        self.common_enums = {args['name']:FieldEnum(**args) for args in source_schema["common_enums"]}

        self.common_fields = []
        for cf in source_schema['common_fields']:
            if 'enum_name' in cf:
                args = {k:cf[k] for k in cf if k != 'enum_name'}
                args['enum'] = self.common_enums[cf['enum_name']]
                self.common_fields.append(Field(**args))

            else:
                self.common_fields.append(Field(**cf))


        print self.common_enums
        print self.common_fields