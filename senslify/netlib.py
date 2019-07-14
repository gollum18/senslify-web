#! /usr/bin/env python3

'''
Defines the networking library for senslify.
'''

from xmlrpc import client

SERVER_PORT = 10075

class SDCPClient:
    '''
    Implements the SDCP protocol on the client side. Clients should
    use this library to talk to the server.
    '''

    def __init__(self, srv_addr):
        '''
        Returns an instance of an SDCPClient that connected to the 
        indicated SDCP server.
        '''
        self.__server = client.Server(srv_addr)
        
        
    def add(self, sensor, make, model, deployment):
        '''
        Attempts to add a sensor to the server.
        '''
        return self.__server.add(sensor, make, model, deployment)
        
    
    def get(self, sensor, rtype, time, num):
        '''
        Attempts to get sensor records from the server.
        '''
        return self.__server.get(sensor, rtype, time, num)
        
    
    def list_deployments(self, num):
        '''
        Attempts to retrieve metadata information on deployments.
        '''
        return self.__server.list_deployments(num)
        
        
    def list_sensors(self, num):
        '''
        Attempts to retrieve information on sensors.
        '''
        return self.__server.list_sensors(num)
    
    
    def push(self, sensor, reading):
        '''
        Attempts to push a reading to the server.
        '''
        return self.__server.push(sensor, reading)
        
        
    def stat_deployment(self, deployment, rtype, month, year):
        '''
        Attempts to retrieve statistics on a deployment.
        '''
        return self.__server.stat_deployment()
        
    
    def stat_sensor(self, sensor, rtype, month, year):
        '''
        Attempts to retrieve statistics for a sensor.
        '''
        return self.__server.stat_sensor(sensor, rtype)
    
    
    def update(self, sensor, deployment):
        '''
        '''
        return self.__server.update(sensor, deployment)


from twisted.web import xmlrpc
        
class SDCPServer(xmlrpc.XMLRPC):
    '''
    Implements the SDCP protocol server side via XML Remote 
    Procedure Calls.
    '''
    
    def SDCPServer(self, db_addr):
        xmlrpc.XMLRPC.__init__()
        
    
    def xmlrpc_add(self, sensor, make, model, deployment):
        '''
        '''
        return 'Implement the add method for the server...'

    
    def xmlrpc_get(self, sensor, rtype, time, num):
        '''
        '''
        return 'Implement the get method for the server...'

    
    def xmlrpc_list_deployments(self, num):
        '''
        '''
        return 'Implement the list deployments method for the server...'

    
    def xmlrpc_list_sensors(self, num):
        '''
        '''
        return 'Implement the list sensors method for the server...'

    
    def xmlrpc_push(self, sensor, reading):
        '''
        '''
        return 'Implement the push method for the server...'


    def xmlrpc_stat_deployment(self, deployment, rtype, month, year):
        '''
        '''
        return 'Implement the stat deployment method for the server...'


    def xmlrpc_stat_sensor(self, sensor, rtype, month, year):
        '''
        '''
        return 'Implement the stat sensor method for the server...' 
    
    
    def xmlrpc_update(self, sensor, deployment):
        '''
        '''
        return 'Implement the update method for the server...'


