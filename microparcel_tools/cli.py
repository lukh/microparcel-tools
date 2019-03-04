# -*- coding: utf-8 -*-

"""Console script for microparcel_tools."""
import sys
import os
import click

import json
from jsoncomment import JsonComment

from tools import validate_protocol_schema
from microparcel_tools import Protocol

from generators import message

@click.command()
@click.argument('schema_file')
@click.option('--cxx', help="CXX Folder destination")
def main(schema_file, cxx=None):
    """Generate serialization/deserialization code from schema"""

    click.echo('Working on file: ' + schema_file)

    # validate file exists
    if not os.path.isfile(schema_file):
        click.echo('File not found')
        return -1

    # loading schema from file
    json_parser = JsonComment(json)
    with open(schema_file) as fd:
        schema = json_parser.load(fd)


    # validating the schema
    status, msg = validate_protocol_schema(schema)
    if not status:
        click.echo('Invalid Schema:' + msg)
        return -2
    click.echo('Schema is valid')


    # Build the protocol
    protocol = Protocol(schema)

    # build CXX
    if cxx is not None:
        if not os.path.isdir(cxx):
            click.echo('CXX Dest not found')
            return -1
        message.make_message_cxx(protocol, cxx)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
