#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `microparcel_tools` package."""


import unittest

import microparcel_tools as mp
from microparcel_tools import cli


class TestMicroparcel_tools(unittest.TestCase):
    """Tests for `microparcel_tools` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_standard_small_fields(self):
        schema = {
            "name":"Test",
            "version":{
                "major":0,
                "minor":1,
            },
            "endpoints":["Master", "Slave"],
            "common_enums":[],
            "common_fields":[],
            "nodes":{
                "name":"Root", 
                "children":[
                    {
                        "name":"Message1",
                        "senders":["Slave"],
                        "fields":[
                            {"name":"Field1", "short_name":"F1", "bitsize":4},
                            {"name":"Field2", "short_name":"F2", "bitsize":4},
                            {"name":"Field3", "short_name":"F3", "bitsize":4},
                            {"name":"Field4", "short_name":"F4", "bitsize":4},
                        ]
                    },
                ]
            }
        }

        p = mp.Protocol(schema)

        self.assertEqual(p.bytesize, 3)

        self.assertEqual(p.fields[0].offset, 0)
        self.assertEqual(p.fields[1].offset, 1)
        self.assertEqual(p.fields[2].offset, 5)
        self.assertEqual(p.fields[3].offset, 9)
        self.assertEqual(p.fields[4].offset, 13)

        self.assertEqual(p.fields[0].bitsize, 1)
        self.assertEqual(p.fields[1].bitsize, 4)
        self.assertEqual(p.fields[2].bitsize, 4)
        self.assertEqual(p.fields[3].bitsize, 4)
        self.assertEqual(p.fields[4].bitsize, 4)

    def test_standard_small_fields_no_root(self):
        schema = {
            "name":"Test",
            "version":{
                "major":0,
                "minor":1,
            },
            "endpoints":["Master", "Slave"],
            "common_enums":[],
            "common_fields":[],
            "nodes":{
                "name":"Message1",
                "senders":["Slave"],
                "fields":[
                    {"name":"Field1", "short_name":"F1", "bitsize":4},
                    {"name":"Field2", "short_name":"F2", "bitsize":4},
                    {"name":"Field3", "short_name":"F3", "bitsize":4},
                    {"name":"Field4", "short_name":"F4", "bitsize":4},
                ]
            }
        }

        p = mp.Protocol(schema)

        self.assertEqual(p.bytesize, 2)

        self.assertEqual(p.fields[0].offset, 0)
        self.assertEqual(p.fields[1].offset, 4)
        self.assertEqual(p.fields[2].offset, 8)
        self.assertEqual(p.fields[3].offset, 12)

        self.assertEqual(p.fields[0].bitsize, 4)
        self.assertEqual(p.fields[1].bitsize, 4)
        self.assertEqual(p.fields[2].bitsize, 4)
        self.assertEqual(p.fields[3].bitsize, 4)


    def test_standard_small_fields_odd(self):
        schema = {
            "name":"Test",
            "version":{
                "major":0,
                "minor":1,
            },
            "endpoints":["Master", "Slave"],
            "common_enums":[],
            "common_fields":[],
            "nodes":{
                "name":"Root", 
                "children":[
                    {
                        "name":"Message1",
                        "senders":["Slave"],
                        "fields":[
                            {"name":"Field1", "short_name":"F1", "bitsize":2},
                            {"name":"Field2", "short_name":"F2", "bitsize":3},
                            {"name":"Field3", "short_name":"F3", "bitsize":1},
                            {"name":"Field4", "short_name":"F4", "bitsize":5},

                            {"name":"Field5", "short_name":"F4", "bitsize":8},
                            {"name":"Field6", "short_name":"F4", "bitsize":7},
                            {"name":"Field7", "short_name":"F4", "bitsize":3},
                        ]
                    },
                ]
            }
        }

        p = mp.Protocol(schema)

        self.assertEqual(p.bytesize, 4)
        # Message1
        self.assertEqual(p.fields[0].offset, 0)
        
        self.assertEqual(p.fields[1].offset, 1)
        self.assertEqual(p.fields[2].offset, 3)
        self.assertEqual(p.fields[3].offset, 6)
        self.assertEqual(p.fields[4].offset, 7)
        self.assertEqual(p.fields[5].offset, 12)
        self.assertEqual(p.fields[6].offset, 20)
        self.assertEqual(p.fields[7].offset, 27)

        self.assertEqual(p.fields[0].bitsize, 1)
        self.assertEqual(p.fields[1].bitsize, 2)
        self.assertEqual(p.fields[2].bitsize, 3)
        self.assertEqual(p.fields[3].bitsize, 1)
        self.assertEqual(p.fields[4].bitsize, 5)
        self.assertEqual(p.fields[5].bitsize, 8)
        self.assertEqual(p.fields[6].bitsize, 7)
        self.assertEqual(p.fields[7].bitsize, 3)


    def test_routing(self):
        schema = {
            "name":"Test",
            "version":{
                "major":0,
                "minor":1,
            },
            "endpoints":["Master", "Slave"],
            "common_enums":[],
            "common_fields":[],
            "nodes":{
                "name":"Root", 
                "children":[
                    {
                        "name":"Message1",
                        "senders":["Slave"],
                        "fields":[
                            {"name":"Field1", "short_name":"F1", "bitsize":2},
                            {"name":"Field2", "short_name":"F2", "bitsize":3},
                        ]
                    },
                    {
                        "name":"Message2",
                        "senders":["Slave"],
                        "fields":[
                            {"name":"Field1", "short_name":"F1", "bitsize":3},
                            {"name":"Field2", "short_name":"F2", "bitsize":2},
                        ]
                    },
                    {
                        "name":"Message3",
                        "children":[
                            {
                                "name":"SubMessage1",
                                "senders":["Slave"],
                                "fields":[
                                    {"name":"Field1", "short_name":"F1", "bitsize":2},
                                    {"name":"Field2", "short_name":"F2", "bitsize":3},
                                ]
                            },
                            {
                                "name":"SubMessage2",
                                "senders":["Slave"],
                                "fields":[
                                    {"name":"Field1", "short_name":"F1", "bitsize":5},
                                    {"name":"Field2", "short_name":"F2", "bitsize":3},
                                ]
                            },
                        ]
                    },
                ]
            }
        }

        p = mp.Protocol(schema)

        self.assertEqual(p.bytesize, 2)

        self.assertEqual(p.fields[0].name, "Root")
        self.assertEqual(p.fields[0].offset, 0)
        self.assertEqual(p.fields[0].bitsize, 2)
        self.assertEqual(p.fields[0].enum.enumerators, ["Message1", "Message2", "Message3"])
        
        self.assertEqual(p.fields[1].name, "Message1Field1")
        self.assertEqual(p.fields[1].offset, 2)
        self.assertEqual(p.fields[1].bitsize, 2)

        self.assertEqual(p.fields[2].name, "Message1Field2")
        self.assertEqual(p.fields[2].offset, 4)
        self.assertEqual(p.fields[2].bitsize, 3)

        self.assertEqual(p.fields[3].name, "Message2Field1")
        self.assertEqual(p.fields[3].offset, 2)
        self.assertEqual(p.fields[3].bitsize, 3)

        self.assertEqual(p.fields[4].name, "Message2Field2")
        self.assertEqual(p.fields[4].offset, 5)
        self.assertEqual(p.fields[4].bitsize, 2)

        self.assertEqual(p.fields[5].name, "Message3")
        self.assertEqual(p.fields[5].offset, 2)
        self.assertEqual(p.fields[5].bitsize, 1)
        self.assertEqual(p.fields[5].enum.enumerators, ["SubMessage1", "SubMessage2"])


        self.assertEqual(p.fields[6].name, "SubMessage1Field1")
        self.assertEqual(p.fields[6].offset, 3)
        self.assertEqual(p.fields[6].bitsize, 2)

        self.assertEqual(p.fields[7].name, "SubMessage1Field2")
        self.assertEqual(p.fields[7].offset, 5)
        self.assertEqual(p.fields[7].bitsize, 3)

        self.assertEqual(p.fields[8].name, "SubMessage2Field1")
        self.assertEqual(p.fields[8].offset, 3)
        self.assertEqual(p.fields[8].bitsize, 5)

        self.assertEqual(p.fields[9].name, "SubMessage2Field2")
        self.assertEqual(p.fields[9].offset, 8)
        self.assertEqual(p.fields[9].bitsize, 3)



    def test_subcat(self):
        schema = {
            "name":"Test",
            "version":{
                "major":0,
                "minor":1,
            },
            "endpoints":["Master", "Slave"],
            "common_enums":[],
            "common_fields":[],
            "nodes":{
                "name":"Root", 
                "children":[
                    {
                        "name":"Message1",
                        "subcat":["Sub1", "Sub2", "Sub3"],
                        "senders":["Slave"],
                        "fields":[
                            {"name":"Field1", "short_name":"F1", "bitsize":4},
                            {"name":"Field2", "short_name":"F2", "bitsize":4},
                            {"name":"Field3", "short_name":"F3", "bitsize":4},
                            {"name":"Field4", "short_name":"F4", "bitsize":4},
                        ]
                    },
                ]
            }
        }

        p = mp.Protocol(schema)
        self.assertEqual(p.bytesize, 3)

        self.assertEqual(p.fields[0].name, "Root")
        self.assertEqual(p.fields[0].offset, 0)
        self.assertEqual(p.fields[0].bitsize, 1)

        self.assertEqual(p.fields[1].name, "Message1")
        self.assertEqual(p.fields[1].offset, 1)
        self.assertEqual(p.fields[1].bitsize, 2)
        self.assertEqual(p.fields[1].enum.enumerators, ["Sub1", "Sub2", "Sub3"])

        self.assertEqual(p.fields[2].offset, 2+1)
        self.assertEqual(p.fields[3].offset, 2+5)
        self.assertEqual(p.fields[4].offset, 2+9)
        self.assertEqual(p.fields[5].offset, 2+13)

        self.assertEqual(p.fields[2].bitsize, 4)
        self.assertEqual(p.fields[3].bitsize, 4)
        self.assertEqual(p.fields[4].bitsize, 4)
        self.assertEqual(p.fields[5].bitsize, 4)


    def test_common_fields(self):
        schema = {
            "name":"Test",
            "version":{
                "major":0,
                "minor":1,
            },
            "endpoints":["Master", "Slave"],
            "common_enums":[
                {"name":"SpeedUnit", "enumerators":["Knot", "KmPerH"]}
            ],

            "common_fields":[
                {"name": "Address", "short_name":"Ad", "bitsize":5},
                {"name": "ProtocolVersion", "short_name":"Pv", "bitsize":9}
            ],

            "nodes":{
                "name":"Root", 
                "senders":["Slave"],
                "fields":[
                    {"name":"Field1", "short_name":"F1", "enum_name":"SpeedUnit"},
                    {"name":"Field2", "short_name":"F1", "enumerators":["A", "B", "C","D"]},
                ]
            }
        }


        p = mp.Protocol(schema)

        # self.assertEqual(p.bytesize, 3)


        self.assertEqual(p.common_fields[0].name, "Address")
        self.assertEqual(p.common_fields[0].offset, 0)
        self.assertEqual(p.common_fields[0].bitsize, 5)

        self.assertEqual(p.common_fields[1].name, "ProtocolVersion")
        self.assertEqual(p.common_fields[1].offset, 5)
        self.assertEqual(p.common_fields[1].bitsize, 9)

        self.assertEqual(p.fields[0].name, "RootField1")
        self.assertEqual(p.fields[0].offset, 14)
        self.assertEqual(p.fields[0].bitsize, 1)


        self.assertEqual(p.fields[1].name, "RootField2")
        self.assertEqual(p.fields[1].offset, 15)
        self.assertEqual(p.fields[1].bitsize, 2)


    def test_standard_big_fields_no_root(self):
        schema = {
            "name":"Test",
            "version":{
                "major":0,
                "minor":1,
            },
            "endpoints":["Master", "Slave"],
            "common_enums":[],
            "common_fields":[],
            "nodes":{
                "name":"Message1",
                "senders":["Slave"],
                "fields":[
                    {"name":"Field1", "short_name":"F1", "bitsize":4},
                    {"name":"Field2", "short_name":"F2", "bitsize":8},
                    {"name":"Field3", "short_name":"F3", "bitsize":13},
                    {"name":"Field4", "short_name":"F4", "bitsize":3},
                ]
            }
        }

        p = mp.Protocol(schema)

        self.assertEqual(p.bytesize, 4)

        self.assertEqual(p.fields[0].offset, 13)
        self.assertEqual(p.fields[0].bitsize, 4)

        self.assertEqual(p.fields[1].offset, 17)
        self.assertEqual(p.fields[1].bitsize, 8)

        self.assertEqual(p.fields[2].offset, 0)
        self.assertEqual(p.fields[2].bitsize, 13)
        
        self.assertEqual(p.fields[3].offset, 25)
        self.assertEqual(p.fields[3].bitsize, 3)


    def test_standard_big_fields_with_inter_no_root(self):
        schema = {
            "name":"Test",
            "version":{
                "major":0,
                "minor":1,
            },
            "endpoints":["Master", "Slave"],
            "common_enums":[],
            "common_fields":[],
            "nodes":{
                "name":"Message1",
                "senders":["Slave"],
                "fields":[
                    {"name":"Field1", "short_name":"F1", "bitsize":4},
                    {"name":"Field2", "short_name":"F2", "bitsize":8},
                    {"name":"Field3", "short_name":"F3", "bitsize":13},
                    {"name":"Field4", "short_name":"F4", "bitsize":2},
                    {"name":"Field5", "short_name":"F5", "bitsize":9},
                    {"name":"Field6", "short_name":"F6", "bitsize":1},
                ]
            }
        }

        p = mp.Protocol(schema)

        self.assertEqual(p.bytesize, 5)

        self.assertEqual(p.fields[0].offset, 25)
        self.assertEqual(p.fields[0].bitsize, 4)

        self.assertEqual(p.fields[1].offset, 29)
        self.assertEqual(p.fields[1].bitsize, 8)

        self.assertEqual(p.fields[2].offset, 0)
        self.assertEqual(p.fields[2].bitsize, 13)
        
        self.assertEqual(p.fields[3].offset, 13)
        self.assertEqual(p.fields[3].bitsize, 2)

        self.assertEqual(p.fields[4].offset, 16)
        self.assertEqual(p.fields[4].bitsize, 9)

        self.assertEqual(p.fields[5].offset, 15)
        self.assertEqual(p.fields[5].bitsize, 1)


    def test_standard_big_fields_no_root_common(self):
        schema = {
            "name":"Test",
            "version":{
                "major":0,
                "minor":1,
            },
            "endpoints":["Master", "Slave"],
            "common_enums":[],
            "common_fields":[
                {"name":"Common", "short_name":"F1", "bitsize":5},

            ],
            "nodes":{
                "name":"Message1",
                "senders":["Slave"],
                "fields":[
                    {"name":"Field1", "short_name":"F1", "bitsize":4},
                    {"name":"Field2", "short_name":"F2", "bitsize":8},
                    {"name":"Field3", "short_name":"F3", "bitsize":13},
                    {"name":"Field4", "short_name":"F4", "bitsize":3},
                ]
            }
        }

        p = mp.Protocol(schema)

        self.assertEqual(p.bytesize, 5)
        self.assertEqual(p.common_fields[0].offset, 0)
        self.assertEqual(p.common_fields[0].bitsize, 5)

        self.assertEqual(p.fields[0].offset, 21)
        self.assertEqual(p.fields[0].bitsize, 4)

        self.assertEqual(p.fields[1].offset, 25)
        self.assertEqual(p.fields[1].bitsize, 8)

        self.assertEqual(p.fields[2].offset, 8)
        self.assertEqual(p.fields[2].bitsize, 13)
        
        self.assertEqual(p.fields[3].offset, 5)
        self.assertEqual(p.fields[3].bitsize, 3)