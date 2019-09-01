# THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
# APPLICABLE LAW. EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
# HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT
# WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE. THE ENTIRE RISK AS TO THE QUALITY AND
# PERFORMANCE OF THE PROGRAM IS WITH YOU. SHOULD THE PROGRAM PROVE
# DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR OR
# CORRECTION.

# Name: btlemon.py
# Since:
# Author: Christen Ford
# Purpose: Linux only. Serves as a bluetooth client for connecting bluetooth low-energy services
#   to the Senslify web server.

import click, os, sys
from bluepy import btle
from click_shell import shell
        
        
# This method was taken from the pybluez implementation.
def is_valid_address(address):
    """Determins if the given MAC address is valid.
    Valid address are always strings of the form XX:XX:XX:XX:XX:XX
    where X is a hexadecimal character.  For example,
    01:23:45:67:89:AB is a valid address, but IN:VA:LI:DA:DD:RE is not.
    
    Arguments:
        address (str): A MAC address.
    """
    try:
        pairs = s.split (":")
        if len (pairs) != 6: return False
        if not all(0 <= int(b, 16) <= 255 for b in pairs): return False
    except:
        return False
    return True


devices = dict()


@shell(prompt='btlemon > ', intro='Welcome to btlemon. Type help to see a list of commands.')
def main():
    pass


@main.command('discover')
@click.option('-i', '--index', default=0, type=click.INT)
@click.option('-t', '--timeout', default=10, type=click.INT)
def device_discover_command(index, timeout):
    """Discovers bluetooth low-energy devices.
    
    Arguments:
        index (int): The index of the bluetooth adapter.
        Bluetooth adapters are recognized on most Linux systems as /dev/hci#
        where # is the index.
        timeout (int): The scanner timeout.
    """
    try:
        click.echo('Now scanning for btle devices...')
        scanner = btle.Scanner(index)
        entries = scanner.scan(timeout)
        click.echo('Found the following btle devices...')
        for entry in entries:
            click.echo(entry.getScanData())
    except btle.BTLEException as e:
        click.secho('A BTLEException has occurred!\n{}'.format(e), fg='red')


@main.group()
def device():
    pass

    
@device.command('chars')
@click.argument('address')
@click.option('-sh', '--start-handle', default=1)
@click.option('-eh', '--end-handle', default=0xFFFF)
@click.option('-u', '--uuid', default=None)
def device_chars_command(address, start_handle, end_handle, uuid):
    """Gets the GATT characteristics of the specified device.
    
    Arguments:
        address (str): The MAC address of the device.
    """
    try:
        # check the mac address
        if is_valid_address(address):    
            global devices
            
            # check that the device exists
            if address in devices:
                click.echo()
                chars = devices[address].getCharacteristics(
                    startHnd=start_handle, endHnd=end_handle,uuid=uuid)
                if chars:
                    for char in chars:
                        if char.supportsRead():
                            click.echo('  {} - {}'.format(char.getHandle(), char.read()))
                        else:
                            click.echo('  {} - read not supported!'.format(char.getHandle()))
                else:
                    click.secho('The device does not specify GATT characteristics.', fg='yellow')
            else:
                click.secho('Command cannot be run. No such device with address {} found!'.format(address), fg='red')
        else:
            click.secho('Command cannot be run. Device MAC {} not valid!'.format(address), fg='red')
    except btle.BTLEException as e:
        click.secho('A BTLEException has occured!\n{}'.format(e), fg='red')
    
    
@device.command('add')
@click.argument('address')
@click.option('-t', '--addr-type', default=btle.ADDR_TYPE_PUBLIC, type=click.STRING)
def device_add_command(address, addr_type):
    """Adds the devicce but does not connect to it.
    
    Arguments:
        address (str): The MAC address of the device.
    """
    try:
        # check the mac address
        if is_valid_address(address):    
            global devices
            
            # check that the device exists
            if address not in devices:
                # check the address type
                if addr_type == btle.ADDR_TYPE_PUBLIC or addr_type == btle.ADDR_TYPE_RANDOM:
                    devices[address] = btle.Peripheral(address=address)
                else:
                    click.secho('Cannot add device, device address type {} not valid!'.format(addr_type), fg='red')
            else:
                click.secho('Command cannot be run. Device {} already exists!'.format(address), fg='red')
        else:
            click.secho('Command cannot be run. Device MAC {} not valid!'.format(address), fg='red') 
    except btle.BTLEException as e:
        click.secho('A BTLEException has occured!\n{}'.format(e), fg='red')
    

@device.command('connect')
@click.argument('address')
def device_connect_command(address):
    """Connects to the specified device.
    
    Arguments:
        address (str): The MAC address of the device.
    """
    # check the mac address
    try:
        if is_valid_address(address):    
            global devices
            
            # check that the device exists
            if address in devices:
                devices[address].connect()
            else:
                click.secho('Command cannot be run. No such device with address {} found!'.format(address), fg='red')
        else:
            click.secho('Command cannot be run. Device MAC {} not valid!'.format(address), fg='red')
    except btle.BTLEException as e:
        click.secho('A BTLEException has occured!\n{}'.format(e), fg='red')


@device.command('disconnect')
@click.argument('address')
def device_disconnect_command(address):
    """Disconnects from the specified device.
    
    Arguments:
        address (str): The MAC address of the device.
    """
    try:
        # check the mac address
        if is_valid_address(address):    
            global devices
            
            # check that the device exists
            if address in devices:
                click.echo('Disconnecting from device {}...'.format(address))
                devices[address].disconnect()
                del devices[address]
                click.echo('Device {} disconnected.'.format(address))
            else:
                click.secho('Command cannot be run. No such device found with address {}!'.format(address), fg='red')
        else:
            click.secho('Command cannot be run. Device MAC {} not valid!'.format(address), fg='red')
    except btle.BTLEException as e:
        click.secho('A BTLEException has occured!\n{}'.format(e), fg='red')
    
@device.command('services')
@click.argument('address')
def device_services_command(address):
    """Prints the services the device offers.
    
    Arguments:
        address (str): The MAC address of the device.
    """
    try:
        # check the mac address
        if is_valid_address(address):    
            global devices
            
            # check that the device exists
            if address in devices:
                click.echo('Getting services for device {}...'.format(address))
                for key, value in devices[address][0].getServices().items():
                    click.echo('  {} - {}'.format(key, value))
                click.echo('All discovered services for devices {} listed.'.format(address))
            else:
                click.secho('Command cannot be run. No such device with address {} found!'.format(address), fg='red')
        else:
            click.secho('Command cannot be run. Device MAC {} not valid!'.format(address), fg='red')
    except btle.BTLEException as e:
        click.secho('A BTLEException has occured!\n{}'.format(e), fg='red')


if __name__ == '__main__':
	main()
