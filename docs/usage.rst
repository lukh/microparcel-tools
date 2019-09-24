=====
Usage
=====

To use microparcel_tools from command line:

.. code-block:: console

    microparcel_tools path/to/schema.json --py path/to/generate/py/dir -cxx path/to/generate/c++/dir

or

.. code-block:: console

    python -m microparcel_tools path/to/schema.json --py path/to/generate/py/dir -cxx path/to/generate/c++/dir


The schemas is the source file, written in JSON. See the examples in examples.
It will generates:
* A Message File: defines all the necessary fields 
* A Router File per endpoint; they provides static "make" methods and pure virtual "process" methods.


basically, it describes nodes and fields.

A node can have children node, it allows to organize messages by subject.
And a node without children (called a Leaf) can have Fields.

The endpoints are the termination of the serial line (eg: Master or Slave).
A message is send by one or more endpoint (defined by sender)
This defines which Endpoint has a "make" method and a "process" method

The microparcel_tool generates, in python or C++, source code to generate microparcel messages, or to process them, in order to send them via a serial line.

This piece of Schema will generate

.. code-block:: console

    "name":"Farm",
    "version":{"major":0, "minor":1},
    "endpoints":["Master", "Slave"],
    "nodes":{
        "name":"MsgType", 
        "children":[
            {
                "name":"Measure",
                "children":[
                    {
                        "name":"Windspeed",
                        "senders":["Slave"],
                        "fields":[
                            {"name":"ID", "short_name":"ID", "bitsize":4},
                            {"name":"Unit", "short_name":"Un", "enum_name":"SpeedUnit"},
                            {"name":"Value", "short_name":"Va", "bitsize":12},
                        ]
                    },


A Master Router

.. code-block:: cpp

    class FarmMasterRouter {
        virtual void processWindspeed(uint8_t in_windspeedid, FarmMsg::SpeedUnit in_windspeedunit, uint16_t in_windspeedvalue) = 0;
    };


A Slave Router

.. code-block:: cpp

    class FarmSlaveRouter {
        static FarmMsg makeWindspeed(uint8_t in_windspeedid, FarmMsg::SpeedUnit in_windspeedunit, uint16_t in_windspeedvalue){
            FarmMsg msg = FarmMsg();

            msg.setAddress(in_address);
            msg.setProtocolVersion(in_protocolversion);

            msg.setMsgType(FarmMsg::MsgType_Measure); 
            msg.setMeasure(FarmMsg::Measure_Windspeed); 

            msg.setWindspeedID(in_windspeedid);
            msg.setWindspeedUnit(in_windspeedunit);
            msg.setWindspeedValue(in_windspeedvalue);

            return msg;
        }
    };


Sending Message
---------------

Creating and sending a message is easy (from Slave side):


.. code-block:: cpp

    #include <microparcel/microparcel.h>
    #include "FarmMsg.h"
    #include "FarmSlaveRouter.h"

    class FarmSlaveRouterImplementation: public FarmSlaveRouter {
        // need to implement all pure virtual process methods for others messages.
        // virtual void process...{
        //}
    };

    // prototype to send data
    void send(uint8_t *data, uint8_t datasize);

    int main(){
        // a Parser for FarmMessage.
        using TParser = microparcel::Parser<FarmMsg::kSize>;

        FarmMsg msg = FarmSlaveRouterImplementation::makeWindspeed(5, FarmMsg::SpeedUnit_Knot, 100);


        // builds the frame, with SOF and checksum
        TParser::Frame_T frame = TParser.encode(msg);

        // send over physical layer of choice
        send((uint8_t*)&inFrame, TFrame::FrameSize);

    }


Receiving message
-----------------

The master side and the slave implements the virtual process methods; where their parameters are the relevant one (windspeed and ID of the measure)

A Router has a "process" methods:

.. code-block:: cpp

    void process(FarmMsg &in_msg){
        // big automatic generated switch-case


Calling "process" with a VALID message received from microparcel 's Parser.parse will call the right virtual processes method.


.. code-block:: cpp

    #include <microparcel/microparcel.h>
    #include "FarmMsg.h"
    #include "FarmMasterRouter.h"

    class FarmMasterRouterImplementation: public FarmMasterRouter {
        virtual void processWindspeed(uint8_t in_windspeedid, FarmMsg::SpeedUnit in_windspeedunit, uint16_t in_windspeedvalue){
            // DO SOMETHING
            notifyViaWifi(in_windspeedid, in_windspeedvalue);
        }
    };

    // a way to get data from a Serial Line (UART ?)
    uint8_t getByteFromDataLine();
    bool isDataLineEmpty();

    int main(){
        // a Parser for FarmMessage.
        using TParser = microparcel::Parser<FarmMsg::kSize>;

        FarmMasterRouterImplementation fmri;
        FarmMsg msg;

        TParser parser;
        TParser::Status status;

        // main loop of embedded application
        while(true){
            // continue till the fifo is empty
            while(!isDataLineEmpty()){
                uint8_t byte = getByteFromDataLine();
                status = parser.parse(byte, &msg);
                switch(status){
                    // not complete and error could be treated differently...
                    // error means mainly that the checksum is not valid; transmission failed.
                    case TParser::eNotComplete:
                    case TParser::eError:
                        break;

                    case TParser::eComplete:
                        // msg is complete, handle it
                        fmri.process(msg);
                        break;
                }
            }

        }
    }
