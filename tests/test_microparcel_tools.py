#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `microparcel_tools` package."""


import unittest
from click.testing import CliRunner

from microparcel_tools import microparcel_tools
from microparcel_tools import cli


class TestMicroparcel_tools(unittest.TestCase):
    """Tests for `microparcel_tools` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        # run failed because no schema input
        result = runner.invoke(cli.main)
        assert result.exit_code != 0

        # test help msg
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output

        # test schemas
        help_result = runner.invoke(cli.main, ['schemas.json'])
        assert help_result.exit_code == 0
