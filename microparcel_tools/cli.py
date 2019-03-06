# -*- coding: utf-8 -*-

"""Console script for microparcel_tools."""
import sys
import os
import argparse
import logging

import json
from jsoncomment import JsonComment

from tools import validate_protocol_schema
from microparcel_tools import Protocol

from generators import message

def main(schema_file, cxx=None):
    """Generate serialization/deserialization code from schema"""
    logging.info('Working on file: ' + schema_file)

    # validate file exists
    if not os.path.isfile(schema_file):
        logging.info('File not found')
        return -1

    # loading schema from file
    json_parser = JsonComment(json)
    with open(schema_file) as fd:
        schema = json_parser.load(fd)


    # validating the schema
    status, msg = validate_protocol_schema(schema)
    if not status:
        logging.info('Invalid Schema:' + msg)
        return -2
    logging.info('Schema is valid')


    # Build the protocol
    protocol = Protocol(schema)

    # build CXX
    if cxx is not None:
        if not os.path.isdir(cxx):
            logging.info('CXX Dest not found')
            return -1
        message.make_message_cxx(protocol, cxx)

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='microparcel parser and message generation tool')
    parser.add_argument('schema_file', type=str, help='schema file, in json format')
    parser.add_argument('--cxx', help='C++ output folder')

    args = parser.parse_args()
    ret = main(args.schema_file, cxx=args.cxx)  # pragma: no cover

    if ret != 0:
        sys.exit(ret)

