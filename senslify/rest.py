# THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
# APPLICABLE LAW. EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
# HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT
# WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE. THE ENTIRE RISK AS TO THE QUALITY AND
# PERFORMANCE OF THE PROGRAM IS WITH YOU. SHOULD THE PROGRAM PROVE
# DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR OR
# CORRECTION.

# Name: rest.py
# Since: Aug. 22nd, 2019
# Author: Christen Ford
# Purpose: Exposes the database connector as a REST API. The primary purpose
#   of this module is to allow ad-hoc interaction with the database connector.
#
# For the methods defined in this module that return data such as find and stats,
#   they will always return data in the body of the Response as a serialized
#   JSON object.

import aiohttp
import simplejson

from senslify.errors import generate_rest_error
from senslify.verify import verify_rest_request


async def find_handler(request, target, params):
    """Defines a handler for the find target.
    
    Args:
        request (aiohttp.web.Request): The request that initiated the REST handler.
        target (str): The target to initiate the find command against.
        params (dict): A dictionary containing parameters for the target.
        
    Returns:
        (aiohttp.web.Response): A Response object containing the results of 
        executing the find_handler as a serialized JSON object in its body.
    """
    # define the results set
    results = []
    
    # target handler for groups
    if target == 'groups':
        for doc in request.app['db'].get_groups():
            results.append(doc)
    # target handler for rtypes
    elif target == 'rtypes':
        for doc in request.app['db'].get_rtypes():
            results.append(doc)
    # target handler for sensors
    elif target == 'sensors':
        groupid = params['groupid']
        for doc in request.app['db'].get_sensors(groupid):
            results.append(doc)
    elif target == 'readings':
        for doc in request.app['db'].get_readings():
            results.append(doc)
    
    # build and return the response
    resp_body = dict()
    resp_body['results'] = results
    return aiohttp.web.Response(body=simplejson.dumps(resp_body))
    

async def stats_handler(request, target, params):
    """Defines a handler for the stats target.
    
    Args:
        request (aiohttp.web.Request): The request that initiated the REST handler.
        target (str): The target to initiate the find command against.
        params (dict): A dictionary containing parameters for the target.
    """
    if target == 'group':
        pass
    elif target == 'sensors':
        pass
    elif target == 'readings':
        pass


async def rest_handler(request):
    """Defines a GET handler for the '/rest' endpoint.

    Users make requests of this handler with a query string containing the following arguments:
        cmd: The command c to execute | c E {find, stats}
        target: The target t to run the command against | t E {groups, rtypes, sensors, readings}.
        params: A list of key-value parameters corresponding to the targets attributes.

    This handler will return an error if the querystring is in an incorrect format.
    
    Args:
        request (aiohttp.web.Request): The web request that initiated the handler.
    """    
    # verify the request
    valid, reason = verify_rest_request(request)
    if not valid:
        return generate_rest_error(reason)
    
    # get the parameters
    cmd = request.query('cmd')
    target = request.query('target')
    params = simplejson.loads(request.query('params'))
    
    # pass off to the correct target handler
    if cmd == 'find':
        response = find_handler(request, target, params)
    elif cmd == 'stats':
        response = stats_handler(request, target, params)
    
    # return the response we get back fgrom the handler
    return response
