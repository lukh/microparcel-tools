# -*- coding: utf-8 -*-
import math

from .common import FieldEnum, Field, Node
from .tools import validate_protocol_schema

class ProtocolVersion(object):
    def __init__(self, major, minor):
        self.major = major
        self.minor = minor

class Protocol(object):
    def __init__(self, source_schema):
        # schema validation
        status, msg = validate_protocol_schema(source_schema)
        if not status:
            raise ValueError(msg)

        # building the protocol
        self.name = source_schema['name']
        self.version = ProtocolVersion(**source_schema['version'])
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

        # nodes
        self.root_node = Node(self.common_enums, None, **source_schema['nodes'])


        # build offsets and bytesize...
        self.bytesize = 0

        # populate fields
        self.fields = []
        def add_node_field(fields_list, node):
            if node.subcat is not None:
                fields_list.append(node.subcat)

            if node.fields is not None:
                for f in node.fields:
                    fields_list.append(f)

            if node.children_field is not None:
                fields_list.append(node.children_field)
                for c in node.children:
                    add_node_field(fields_list, c)

        add_node_field(self.fields, self.root_node)



        ## set offset
        curr_off = 0
        # build common fields
        for cf in self.common_fields:
            cf.offset = curr_off
            curr_off += cf.bitsize

        offsets = []
        for sender in self.endpoints:
            for leaf in self.root_node.leafs(sender):
                off = leaf.build(curr_off)
                offsets.append(off)

        off_max = max(offsets)
        self.bytesize = int(math.ceil(off_max / 8.0))


