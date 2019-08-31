# THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
# APPLICABLE LAW. EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
# HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM “AS IS” WITHOUT
# WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE. THE ENTIRE RISK AS TO THE QUALITY AND
# PERFORMANCE OF THE PROGRAM IS WITH YOU. SHOULD THE PROGRAM PROVE
# DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR OR
# CORRECTION.

# Name: btlecli.py
# Author: Christen Ford
# Since: Aug. 31st, 2019
# Purpose: Meant to act as a client for bluetooth enabled sensors to communicate with the Senslify server. Obviously, you need to have a bluetooth receiver installed on your machine to use this program. The sensors need to be BLE enabled.
# Since this script directly accesses hardware on your machine (through libraries), you'll most likely need to run this wth sudo (if on Linux/Mac) or as an administrator (if on Windows) to actually do anything. 

# For an excellent introduction on Pythons bluetooth functionality see: http://blog.kevindoran.co/bluetooth-programming-with-python-3/

import asyncio, os, sys
import aiohttp
import click
import threading
import uvloop

import bluetooth
from click_shell import shell


#
# SUPPORT CLASSES
#


class BluetoothServer:
    """Defines a simple Bluetooth Server for communicating with Bluetooth-enabled devices."""

    class BluetoothDevice(threading.Thread):
        """Defines a listen-only bluetooth device."""
    
        def __init__(self, addr, callback, size=1024):
            """Returns a new BluetoothDevice object.
            
            Arguments:
                addr (str): The MAC address of the remote bluetooth device.
                callback (function pointer): The callback function to execute when data is read from the device.
                size (int): The amount of data in bytes to receive from the bluetooth device in a single read call.
            """
            self.addr = mac_addr
            
        def run(self):
            """Starts listening for data over the Bluetooth connection."""
            pass


    def __init__(self, addr, port=3, backlog=1, proto=bluetooth.RFCOMM):
        """Returns a new BluetoothServer object.
        
        Arguments:
            addr (str): The MAC address of the servers bluetooth adapter.
            port (int): The port (a COMM/Serial port) to use for the server.
            backlog (int): The number of pending connections to queue up.
            proto (int): The Bluetooth protocol to use for the server (default: bluetooth.RFCOMM).
        """
        self.addr = addr
        self.port = port
        self.backlog = backlog
        self.proto = proto
        self.devices = dict()
        
        
    def add_device(self, addr, callback, size=1024):
        """Adds a device to the servers list of devices.
        
        Arguments:
            addr (str):
            callback (function pointer):
            size (int):
        """
        pass
    
    
    def remove_device(self, addr):
        """Removes the specified device from the servers list of devices.
        
        Arguments:
            addr (str):
        """
        pass


#
# CLIENT COMMANDS
#


@shell(prompt='btlecli > ', intro='Welcome to btrecv. Type \'help\' to see a list of available commands.')
def client():
    """Launches the btrecv command shell."""
    pass
    

def main():
    """Serves as the main entry point into the program."""
    client()


if __name__ == '__main__':
    main()
