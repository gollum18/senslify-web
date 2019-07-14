#! /usr/bin/env python3

from senslify import netlib
        
def main():
    from twisted.internet import endpoints, reactor
    from twisted.web import server
    r = netlib.SDCPServer()
    endpoint = endpoints.TCP4ServerEndpoint(reactor, netlib.SERVER_PORT)
    endpoint.listen(server.Site(r))
    reactor.run()
    
if __name__ == '__main__':
    main()
