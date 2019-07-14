#! /usr/bin/env python3

'''
Implements a command line interface for the SDCP protocol.
'''

import click
from click_shell import shell

from senslify import netlib

# stores local context variables that get passed as neccessary
#   not the best way to do it, but I can't find enough docs on 
#   clicks context variable to ensure it does something similar
config = dict()


@shell(prompt='SDCP: ')
def sdcp():
    '''
    Opaquely constructs and starts the SDCP shell.
    Do not modify this method, it is intentionally passed.
    '''
    pass
    

@sdcp.command()
@click.argument('sensor')
@click.argument('make')
@click.argument('model')
@click.argument('deployment')
def add(sensor, make, model, deployment):
    '''
    Adds a record to the database.
    Arguments:
        sensor:
        make:
        model:
        deployment:
    '''
    pass
    

@sdcp.command()
@click.argument('sensor')
@click.argument('month')
@click.argument('year')
@click.option('--rtype', '-rt', help='The type of record to stat.\nValid record types include:\n\t{light, temp, humid, gyro, accel}')
@click.option('--time', '-t', help='The time frame to retrieve records for.\nMust be in military time with format \'from:to\'\nValid times are in the range [0000, 2400).')
@click.argument('num')
def get(sensor, rtype, month, year, time, num):
    '''
    Gets a number of records from the database for a sensor.
    '''
    pass
    

@sdcp.group()
def list():
    '''
    Defines the \'list\' group. This method should not be called 
    directly.
    '''
    pass
    
    
@list.command()
def deployments():
    '''
    Lists all deployments.
    '''
    pass


@list.command()
@click.argument('deployment')
def sensors(deployment):
    '''
    Lists sensors for a deployment.
    Argument:
        deployment:
    '''
    pass


@sdcp.command()
@click.argument('sensor')
@click.argument('reading')
def push(sensor, reading):
    '''
    Pushes a record to the database.
    Arguments:
        sensor:
        reading:
    '''
    pass
    

@sdcp.group()
def stat():
    '''
    Header method for the \'stat\' group. Do not call directly.
    '''
    pass
    

@stat.command()
@click.argument('deployment')
def deployment(deployment, rtype, month, year):
    '''
    Gets statistics on a deployment.
    Arguments:
        deployment:
        rtype:
        month:
        year:
    '''
    pass
    

@stat.command()
@click.argument('sensor')
@click.option('--rtype', '-rt', help='The type of record to stat.\nValid record types include:\n\t{light, temp, humid, gyro, accel}')
@click.option('--month', '-m', help='The month to get stats on.\nValid months include: {1 ... 12}.')
@click.option('--year', '-y', help='The year to get stats for.')
def sensor(sensor, rtype, month, year):
    '''
    Gets statistics on a sensor.
    Arguments:
        sensor:
        rtype:
        month:
        year:
    '''
    pass
    

@sdcp.command()
@click.argument('deployment')
def update(sensor, deployment):
    '''
    Updates the deployment status of a sensor in the database.
    Arguments:
        sensor: The ID of the sensor to update.
        deployment: The new deployment value.
    '''
    pass
    

def main():
    global config
    
    # Christen - I think the better option here is to use a config 
    #   file and just load it in.
    addr = click.prompt('Enter the address of the senslify server you want to connect to (ex. http://localhost:10075): ')
    # TODO: Verify that the address is reachable
    # Connect to the server
    config['client'] = netlib.SDCPClient(
    'http://localhost:{}'.format(netlib.SERVER_PORT))
    
    # starts the interactive shell
    sdcp()
    
    
if __name__ == '__main__':
    sdcp()
